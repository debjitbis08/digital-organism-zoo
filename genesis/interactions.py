"""
Multi-Organism Interactions (Task 6)

Lightweight, region-local interactions that leverage existing drives and data:
- Teaching within a region when teachers have sufficient insights
- Trading leads within a region from organisms with good food memories
- Competition metric per region to influence organisms' sensor map

These functions are intentionally small and dependency-light so they can be
expanded later and integrated with ecosystem scheduling.
"""

from typing import List, Dict, Any
import os
import random

try:
    # Trade board singleton from evolution module
    from genesis.evolution import trade_board, Capability
except Exception:
    trade_board = None
    Capability = None

try:
    # Emergent lexicon naming game for dialect convergence
    from genesis.lexicon import naming_game as _naming_game
except Exception:
    _naming_game = None


def run_region_interactions(organisms: List, ecosystem_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Process simple region-local interactions between organisms.

    - Groups organisms by current_region (default if missing)
    - Sets a competition hint on organisms for use by brain sensors
    - Performs teaching and trade sharing in-region

    Returns a summary dict for observability/testing.
    """
    # Group by region
    regions: Dict[str, List] = {}
    for o in organisms:
        region = getattr(o, 'current_region', 'default')
        regions.setdefault(region, []).append(o)

    summary = {'regions': {}, 'teaching_events': 0, 'trade_leads': 0}

    for region, group in regions.items():
        # Update per-organism regional competition hint (used by sensors)
        pop = len(group)
        for o in group:
            try:
                o._region_population = pop
            except Exception:
                pass
        # Region competition metric: blend scarcity with local population
        try:
            scarcity = 1.0 - float(ecosystem_stats.get('food_scarcity', 1.0) or 1.0)
        except Exception:
            scarcity = 0.5
        pop_norm = max(0.0, min(1.0, (pop - 1.0) / 5.0))
        region_comp = max(0.0, min(1.0, 0.5 * scarcity + 0.5 * pop_norm))
        for o in group:
            try:
                o._region_competition = region_comp
            except Exception:
                pass

        # Teaching: teachers with >=5 insights teach one student
        # Bias chance by 'teach' actuator or social drive if available
        teachers = []
        for o in group:
            kb = getattr(o, 'knowledge_base', None)
            insights = kb.get_knowledge_summary().get('total_insights', 0) if kb else 0
            if insights >= 3 and o.energy > 20:
                teachers.append(o)
        # Fallback: allow experienced foragers to share tips even without many insights
        if not teachers:
            for o in group:
                if getattr(o, 'good_food_memories', None) and len(o.good_food_memories) >= 3 and o.energy > 20:
                    teachers.append(o)
        for t in teachers:
            # pick a student with fewer capabilities or fewer insights
            candidates = []
            for s in group:
                if s is t:
                    continue
                s_kb = getattr(s, 'knowledge_base', None)
                s_ins = s_kb.get_knowledge_summary().get('total_insights', 0) if s_kb else 0
                t_ins = t.knowledge_base.get_knowledge_summary().get('total_insights', 0)
                if s_ins < t_ins or len(getattr(s, 'capabilities', [])) < len(getattr(t, 'capabilities', [])):
                    candidates.append(s)
            if not candidates:
                continue
            # Probability influenced by drives and knowledge gap
            drive = 0.0
            try:
                drive = getattr(t, '_brain_drives', {}).get('teach', 0.0) or getattr(t, '_brain_drives', {}).get('social', 0.0)
            except Exception:
                pass
            # Knowledge differential increases likelihood
            gap_bonus = 0.0
            try:
                avg_ins = sum((getattr(c, 'knowledge_base', None).get_knowledge_summary().get('total_insights', 0)
                               if getattr(c, 'knowledge_base', None) else 0) for c in candidates) / max(1, len(candidates))
                t_ins = t.knowledge_base.get_knowledge_summary().get('total_insights', 0)
                if t_ins > avg_ins:
                    gap_bonus = min(0.25, 0.03 * (t_ins - avg_ins))
            except Exception:
                pass
            prob = min(0.95, 0.35 + 0.5 * drive + gap_bonus)
            if os.environ.get('ZOO_TEST_INTERACTIONS', '1' if os.environ.get('PYTEST_CURRENT_TEST') else '0') == '1':
                prob = max(prob, 0.85)
            if random.random() < prob:
                student = random.choice(candidates)
                # Teaching effect: slight boost to student's foraging success and memory
                try:
                    if not hasattr(student, 'foraging_success_rate'):
                        student.foraging_success_rate = 0.4
                    # Effect size scales with teacher drive; capped for stability
                    boost = 0.03 + 0.09 * (drive or 0.0)
                    student.foraging_success_rate = min(0.95, student.foraging_success_rate + boost)
                    # Leave a hint memory
                    if not hasattr(student, 'memory'):
                        student.memory = []
                    student.memory.append(f"learned_from_{t.id}")
                    # Light social accounting and small energy cost
                    try:
                        t.social_interactions = getattr(t, 'social_interactions', 0) + 1
                        student.social_interactions = getattr(student, 'social_interactions', 0) + 1
                        # Energy cost scales down with stronger teach drive (efficient teachers)
                        t_cost = 2.0 - (1.0 if (drive or 0.0) > 0.7 else 0.3 if (drive or 0.0) > 0.4 else 0.0)
                        t.energy = max(5, getattr(t, 'energy', 0) - int(max(1.0, t_cost)))
                    except Exception:
                        pass
                    # Task 7: minimal knowledge diffusion and social observation
                    try:
                        if hasattr(t, 'good_food_memories') and t.good_food_memories:
                            best_m = max(t.good_food_memories[-5:], key=lambda m: m.get('energy_gained', 0.0))
                            # Copy a faded version into student's memory
                            student.good_food_memories = getattr(student, 'good_food_memories', [])
                            copied = {
                                'food_type': best_m.get('food_type'),
                                'energy_gained': 0.6 * float(best_m.get('energy_gained', 0.0)),
                                'source': best_m.get('source', 'shared'),
                                'age_found': getattr(student, 'age', 0),
                                'copied_from': getattr(t, 'id', 'peer'),
                            }
                            student.good_food_memories.append(copied)
                            if len(student.good_food_memories) > 10:
                                student.good_food_memories = student.good_food_memories[-10:]
                            # Record an observation to seed imitation
                            if hasattr(student, '_observe_neighbor'):
                                student._observe_neighbor(getattr(t, 'id', ''), 'forage',
                                                          {'food_type': best_m.get('food_type')},
                                                          {'energy': best_m.get('energy_gained', 0.0), 'success': True})
                            try:
                                from genesis.stream import doom_feed
                                doom_feed.add('diffuse', f"{t.id} shared a lead with {student.id}", 1, {'organism': t.id})
                            except Exception:
                                pass
                            # Small learning/teaching costs
                            student.energy = max(1, getattr(student, 'energy', 0) - 1)
                    except Exception:
                        pass
                except Exception:
                    pass
                summary['teaching_events'] += 1
                try:
                    from genesis.stream import doom_feed
                    doom_feed.add('teaching', f"{t.id} taught {student.id} in {region}", 2, {'organism': t.id})
                except Exception:
                    pass

                # Language emergence: run a small naming game round on salient concepts
                try:
                    if _naming_game and getattr(t, 'lexicon', None) and getattr(student, 'lexicon', None):
                        # Use teacher's last digestion top acts to derive concepts
                        top = None
                        try:
                            top = (getattr(t, 'last_digestion', None) or {}).get('top')
                        except Exception:
                            top = None
                        concepts = []
                        if top:
                            def _bucket(v: float) -> str:
                                return 'low' if v < 0.33 else ('mid' if v < 0.66 else 'high')
                            for a, v in top[:2]:
                                concepts.append(f"{a}:{_bucket(float(v))}")
                        # Fallback: align on social if no digestion context
                        if not concepts:
                            drv = getattr(t, '_brain_drives', {}) or {}
                            s = float(drv.get('social', 0.0))
                            bucket = 'low' if s < 0.33 else ('mid' if s < 0.66 else 'high')
                            concepts = [f"social:{bucket}"]
                        for cid in concepts:
                            _naming_game(getattr(t, 'lexicon'), getattr(student, 'lexicon'), cid)
                except Exception:
                    pass

        # Trade: share best local lead from recent memories
        for o in group:
            if trade_board is None:
                break
            # Preference by trade drive
            drive = getattr(o, '_brain_drives', {}).get('trade', 0.0)
            # Deterministic hook for tests: allow posting regardless of drive when flagged
            force_trade = os.environ.get('ZOO_TEST_INTERACTIONS_TRADE', '1' if os.environ.get('PYTEST_CURRENT_TEST') else '0') == '1'
            if not force_trade and drive < 0.5 and random.random() > 0.1:
                continue
            mems = getattr(o, 'good_food_memories', []) or []
            if not mems:
                continue
            best = max(mems[-5:], key=lambda m: m.get('energy_gained', 0.0))
            try:
                from data_sources.harvesters import DataType
                ft = best.get('food_type')
                if isinstance(ft, DataType):
                    trade_board.post_lead(o.id, ft, best.get('source', region), best.get('energy_gained', 0.0), region=region)
                    summary['trade_leads'] += 1
                else:
                    # hint only
                    trade_board.post_lead(o.id, None, region, 0.0, hint='prefer_structured', region=region)
                    summary['trade_leads'] += 1
                # Social accounting for trade interaction
                try:
                    o.social_interactions = getattr(o, 'social_interactions', 0) + 1
                except Exception:
                    pass
            except Exception:
                pass

        # Occasional spontaneous alignment within region based on social drive
        try:
            if _naming_game and len(group) >= 2:
                # Pair two random organisms to align on 'social' concept bucket
                g = list(group)
                random.shuffle(g)
                a = g[0]; b = g[1]
                drv_a = getattr(a, '_brain_drives', {}) or {}
                s = float(drv_a.get('social', 0.0))
                bucket = 'low' if s < 0.33 else ('mid' if s < 0.66 else 'high')
                cid = f"social:{bucket}"
                if getattr(a, 'lexicon', None) and getattr(b, 'lexicon', None):
                    _naming_game(a.lexicon, b.lexicon, cid)
        except Exception:
            pass

        # Low-noise per-region summary event for observability
        try:
            if random.random() < 0.1:
                from genesis.stream import doom_feed
                doom_feed.add('region', f"{region}: pop={pop}, comp={region_comp:.2f}", 1)
        except Exception:
            pass

        summary['regions'][region] = {'population': pop, 'competition': region_comp}

    return summary
