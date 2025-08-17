"""
Runtime ecosystem entrypoint.

This file boots the real-data DataEcosystem (RSS, APIs, file watcher)
and exposes a tiny HTTP interface for health and stats.

It intentionally keeps logic minimal: harvesting runs in a background
thread inside DataEcosystem. The HTTP server simply reports status.
"""
from __future__ import annotations

import os
import signal
from typing import Any, Dict

from flask import Flask, jsonify

try:
    # Optional: used in README and tests/utilities
    from data_sources.harvesters import DataEcosystem
except Exception:  # pragma: no cover - import guard for runtime
    DataEcosystem = None  # type: ignore


def build_config_from_env() -> Dict[str, Any]:
    cfg: Dict[str, Any] = {}
    # Allow faster demo via HARVEST_INTERVAL env var
    hi = os.getenv('HARVEST_INTERVAL')
    if hi is not None:
        try:
            cfg['harvest_interval'] = max(1, int(hi))
        except Exception:
            pass
    # Optional max food storage override
    mfs = os.getenv('MAX_FOOD_STORAGE')
    if mfs is not None:
        try:
            cfg['max_food_storage'] = max(100, int(mfs))
        except Exception:
            pass
    return cfg


class RuntimeManager:
    """Optional runtime state: ticks and organism summary."""
    def __init__(self):
        self.ticks = 0
        self.alive = 0
        self.avg_energy = 0.0
        self.avg_brain_size = 0.0
        # Doom feed integration for exposing chatter
        self._last_feed_index = 0
        self.chatter_recent: list[str] = []

    def snapshot(self) -> Dict[str, Any]:
        # Deduplicate chatter (preserve order, latest kept)
        recent = list(self.chatter_recent[-30:])
        seen = set()
        unique_rev = []
        for msg in reversed(recent):
            if msg not in seen:
                seen.add(msg)
                unique_rev.append(msg)
        unique = list(reversed(unique_rev))
        return {
            'ticks': self.ticks,
            'alive': self.alive,
            'avg_energy': round(self.avg_energy, 3),
            'avg_brain_size': round(self.avg_brain_size, 2),
            'chatter': unique[-10:],
        }


def create_app(eco: Any | None = None, runtime: RuntimeManager | None = None) -> Flask:
    app = Flask(__name__)

    if eco is None:
        if DataEcosystem is None:
            eco = None
        else:
            eco = DataEcosystem(build_config_from_env())

    @app.get('/health')
    def health():  # pragma: no cover - runtime only
        payload = {'ok': True, 'harvesting': bool(eco)}
        if runtime is not None:
            payload.update(runtime.snapshot())
        return jsonify(payload)

    @app.get('/')
    def root():  # pragma: no cover - runtime only
        # Friendly landing page with minimal info
        if eco is None:
            return jsonify({'message': 'Data ecosystem unavailable', 'endpoints': ['/health', '/stats']}), 503
        base = {'message': 'Digital Organism Zoo - DataEcosystem online', 'endpoints': ['/health', '/stats']}
        if runtime is not None:
            base.update({'runtime': runtime.snapshot()})
        return jsonify(base)

    @app.get('/stats')
    def stats():  # pragma: no cover - runtime only
        if eco is None:
            return jsonify({'error': 'DataEcosystem unavailable'}), 503
        try:
            stats = eco.get_ecosystem_stats()
            if runtime is not None:
                stats = dict(stats)
                stats['runtime'] = runtime.snapshot()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Graceful shutdown: terminate harvest thread on SIGTERM
    def _stop(*_args):  # pragma: no cover - runtime only
        try:
            if eco is not None:
                eco.stop()
        finally:
            os._exit(0)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    return app


if __name__ == '__main__':  # pragma: no cover - runtime only
    port = int(os.getenv('PORT', '8080'))
    host = os.getenv('HOST', '0.0.0.0')
    app = create_app()
    # Disable reloader to avoid duplicate threads in container
    app.run(host=host, port=port, debug=False, use_reloader=False)
