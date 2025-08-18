from __future__ import annotations

import json
import time
from typing import Iterator, List, Dict, Any

from flask import Flask, Response, request, send_from_directory

# Ensure repo root is importable when running as a script (python web_interface/server.py)
import os
import sys
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from genesis.stream import doom_feed
from genesis.persistence import create_persistence_system, auto_save_organisms


app = Flask(__name__, static_folder='.', static_url_path='')

# --- Optional: start evolution runtime automatically in web deployments ---
# When this module is imported by a WSGI server (e.g., `flask run`), the
# __main__ block below does not execute. That would previously prevent the
# evolution loop from starting unless the script was launched directly with
# --demo-evolution. We make startup idempotent and optionally automatic so the
# loop can be started both from CLI and when the app is served by Flask.
_evolution_started = False
_evolution_lock = None  # initialized lazily to avoid importing threading early

def start_evolution_runtime() -> None:
    """Start the DataEcosystem + evolution loop and mount its API at /eco.

    Safe to call multiple times; only the first call will perform startup.
    """
    global _evolution_started, _evolution_lock
    if _evolution_lock is None:
        import threading as _threading
        _evolution_lock = _threading.Lock()
    with _evolution_lock:
        if _evolution_started:
            return
        try:
            from genesis.ecosystem import (
                create_app as _create_eco_app,
                RuntimeManager as _RuntimeManager,
                build_config_from_env as _build_cfg,
            )
            from data_sources.harvesters import DataEcosystem as _DataEcosystem
            from genesis.nutrition import create_enhanced_nutrition_system as _create_nutrition
            from genesis.parent_care import ActiveParentCareSystem as _ParentCare
            from genesis.evolution import Organism as _Organism, Capability as _Cap
            from werkzeug.middleware.dispatcher import DispatcherMiddleware as _Dispatcher
            import threading as _threading
            import signal as _signal

            doom_feed.add('system', 'starting evolution runtime (mounted at /eco)', 1)

            # Base config with reasonable defaults; allow env to override
            _cfg = {
                'rss_feeds': ['https://hnrss.org/frontpage'],
                'watch_paths': ['/tmp'],
                'harvest_interval': 10,
                'max_food_storage': 300,
                'scarcity_threshold': 80,
            }
            _env_cfg = _build_cfg()
            _cfg.update(_env_cfg)
            eco = _DataEcosystem(_cfg)

            runtime = _RuntimeManager()
            # Persistence system and state restoration
            persistence_system = create_persistence_system()
            latest = persistence_system.get_latest_generation_save()
            if latest:
                try:
                    organisms = persistence_system.load_generation(latest['file_path'])
                except Exception:
                    organisms = []
                if not organisms:
                    organisms = [_Organism(generation=0) for _ in range(3)]
                current_generation = int(latest.get('generation', 0))
                doom_feed.add('persistence', f"resumed {len(organisms)} organisms from gen {current_generation}", 1)
            else:
                organisms = [_Organism(generation=0) for _ in range(3)]
                current_generation = 0
                doom_feed.add('persistence', f"fresh start with {len(organisms)} organisms", 1)
            for o in organisms:
                try:
                    o.capabilities.add(_Cap.REMEMBER)
                except Exception:
                    pass
            nutrition_system = _create_nutrition()
            parent_care = _ParentCare()

            _stop_flag = _threading.Event()
            _save_lock = _threading.Lock()

            def _brain_params(brain) -> int:
                try:
                    topo = getattr(brain, 'topology', {})
                    return int(topo.get('hid', 0))
                except Exception:
                    return 0

            def _save_state(tag: str = 'periodic') -> None:
                # Save organisms and keep latest pointer updated; safe across threads
                try:
                    with _save_lock:
                        auto_save_organisms(organisms, persistence_system, current_generation)
                        doom_feed.add('persistence', f"state saved ({tag})", 1)
                except Exception as _e:
                    try:
                        doom_feed.add('error', f"save failed: {_e}", 3)
                    except Exception:
                        pass

            def _loop():
                import time as _time
                ticks_since_save = 0
                while not _stop_flag.is_set():
                    try:
                        runtime.ticks += 1
                        ticks_since_save += 1
                        for o in list(organisms):
                            o.live(eco, nutrition_system, parent_care)
                            if o.energy <= 0:
                                try:
                                    organisms.remove(o)
                                except ValueError:
                                    pass
                        a = len(organisms)
                        runtime.alive = a
                        runtime.avg_energy = (sum(o.energy for o in organisms) / a) if a else 0.0
                        sizes = []
                        for o in organisms:
                            b = getattr(o, 'brain', None)
                            if b is not None:
                                sizes.append(_brain_params(b))
                        runtime.avg_brain_size = (sum(sizes) / len(sizes)) if sizes else 0.0
                        # Periodic autosave (roughly every ~25s at 0.5s per tick)
                        if ticks_since_save >= 50:
                            _save_state('autosave')
                            ticks_since_save = 0
                        # Pull some chatter from doom_feed
                        try:
                            events = doom_feed.get_recent(200)
                            msgs = [e.get('message','') for e in events if e.get('tag') == 'chatter']
                            for m in msgs:
                                if m and (not runtime.chatter_recent or runtime.chatter_recent[-1] != m):
                                    runtime.chatter_recent.append(m)
                                    if len(runtime.chatter_recent) > 50:
                                        runtime.chatter_recent = runtime.chatter_recent[-50:]
                        except Exception:
                            pass
                        # Low-noise periodic summary to doom feed so UI always shows activity
                        if runtime.ticks % 10 == 0:
                            try:
                                from genesis.stream import doom_feed as _feed
                                _feed.add('eco', f"tick {runtime.ticks}: alive={a}, avgE={runtime.avg_energy:.2f}, brain={runtime.avg_brain_size:.1f}", 1)
                            except Exception:
                                pass
                    except Exception as e:
                        try:
                            doom_feed.add('error', f'evolution loop error: {e}', 3)
                        except Exception:
                            pass
                    finally:
                        _time.sleep(0.5)

            t2 = _threading.Thread(target=_loop, name='evolution-loop', daemon=True)
            t2.start()

            eco_app = _create_eco_app(eco, runtime)
            # Mount ecosystem app at /eco
            app.wsgi_app = _Dispatcher(app.wsgi_app, {'/eco': eco_app})

            # Register graceful shutdown to persist state on SIGINT/SIGTERM
            def _shutdown_handler(*_args):
                try:
                    _stop_flag.set()
                    _save_state('shutdown')
                finally:
                    os._exit(0)

            try:
                _signal.signal(_signal.SIGTERM, _shutdown_handler)
                _signal.signal(_signal.SIGINT, _shutdown_handler)
            except Exception:
                # Some environments may disallow setting signal handlers
                pass

            # Also attempt to save at interpreter exit
            try:
                import atexit as _atexit
                _atexit.register(lambda: _save_state('atexit'))
            except Exception:
                pass
            _evolution_started = True
        except Exception as e:
            try:
                doom_feed.add('error', f'failed to start evolution runtime: {e}', 3)
            except Exception:
                pass

@app.before_request
def _auto_start_evolution_if_enabled():
    # Enabled by default so that `flask run --app web_interface/server.py` will
    # still start the evolution loop. Opt out by setting ZOO_DISABLE_EVOLUTION=1.
    disabled = os.getenv('ZOO_DISABLE_EVOLUTION', '0') == '1'
    enable_flag = os.getenv('ZOO_AUTO_EVOLUTION', '1') == '1'
    if not disabled and enable_flag:
        start_evolution_runtime()


def _to_ndjson(events: List[Dict[str, Any]]) -> Iterator[bytes]:
    for evt in events:
        yield (json.dumps(evt, ensure_ascii=False) + "\n").encode('utf-8')


@app.get('/events')
def events_ndjson() -> Response:
    """
    NDJSON endpoint for doom feed.
    Query params:
      - since: last seen id (int); 0 for recent tail
      - wait: if '1', long-poll up to ~25s for new events
      - limit: max events to return (default 200)
    """
    last_id = int(request.args.get('since', '0') or '0')
    limit = int(request.args.get('limit', '200') or '200')
    wait_flag = request.args.get('wait', '0') == '1'
    if wait_flag:
        events = doom_feed.wait_for(last_id, timeout=25.0, limit=limit)
    else:
        events = doom_feed.get_since(last_id, limit=limit)
    body = b''.join(_to_ndjson(events))
    return Response(body, mimetype='application/x-ndjson', headers={'Cache-Control': 'no-cache'})


def _sse_format(evt: Dict[str, Any]) -> bytes:
    # Send all events as default 'message' type for broad client compatibility
    data = json.dumps(evt, ensure_ascii=False)
    msg = f"id: {evt.get('id','')}\ndata: {data}\n\n"
    return msg.encode('utf-8')


@app.get('/events/stream')
def events_sse() -> Response:
    """
    Server-Sent Events stream for doom feed. Starts from tail.
    """
    # Start after the most recent event id we know
    recent = doom_feed.get_recent(1)
    start_id = recent[-1]['id'] if recent else 0

    def gen() -> Iterator[bytes]:
        # Send a hello event for clients to confirm connection
        hello = {
            'id': start_id,
            'ts': time.time(),
            'tag': 'hello',
            'message': 'doom stream connected',
            'importance': 0,
            'meta': {}
        }
        yield _sse_format(hello)
        for evt in doom_feed.stream(start_id=start_id):
            yield _sse_format(evt)

    return Response(gen(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive',
    })


@app.get('/doom')
def doom_page() -> Response:
    return send_from_directory('.', 'doom.html')


if __name__ == '__main__':
    import argparse
    import threading
    import random as _random

    parser = argparse.ArgumentParser(description='Doom Feed server with optional simple environment demo.')
    parser.add_argument('--demo-simple', action='store_true', help='Start a simple grid-world environment demo in the background.')
    parser.add_argument('--demo-evolution', action='store_true', help='Start the internet-backed evolution runtime and mount its HTTP API at /eco.')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    if args.demo_simple:
        try:
            from genesis.environment import SimpleEnvironment
            def _run_demo():
                doom_feed.add('system', 'starting simple environment demo', 1)
                rng = _random.Random(42)
                env = SimpleEnvironment(
                    width=30, height=18,
                    K=10.0, r=0.25, noise_std=0.02,
                    bite=1.0, sense_radius=1,
                    base_cost=0.08, mem_cost=0.02,
                    signal_cost=0.03, signal_threshold=1.0,
                    reproduce_threshold=15.0,
                    rng=rng,
                )
                # Seed a couple regions with slightly different parameters
                env.set_regions({
                    'north': (0, 0, 30, 9),
                    'south': (0, 9, 30, 18),
                })
                env.set_region_params('north', K=11.0, r=0.22, noise_std=0.01)
                env.set_region_params('south', K=9.0, r=0.28, noise_std=0.03)
                # Populate organisms
                for _ in range(16):
                    env.add_organism(x=rng.randrange(0, 30), y=rng.randrange(0, 18), energy=6.0, M=rng.choice([2,3,4]), epsilon=0.25, honesty=0.8)
                # Step forever
                import time as _time
                while True:
                    env.step()
                    _time.sleep(0.2)
            t = threading.Thread(target=_run_demo, name='simple-env', daemon=True)
            t.start()
        except Exception as e:
            doom_feed.add('error', f'failed to start demo: {e}', 3)

    # Start the evolution runtime immediately when running as a script unless
    # explicitly disabled. The --demo-evolution flag forces it on.
    if args.demo_evolution or (os.getenv('ZOO_DISABLE_EVOLUTION', '0') != '1' and os.getenv('ZOO_AUTO_EVOLUTION', '1') == '1'):
        start_evolution_runtime()

    doom_feed.add('system', 'doom stream starting', importance=1)
    app.run(host='0.0.0.0', port=args.port, debug=False, threaded=True)
