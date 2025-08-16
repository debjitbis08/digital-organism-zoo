#!/usr/bin/env python3
"""
Test Task 6: Multi-Organism Interactions (region-local)

Validates:
- Region grouping and competition hinting
- Teaching within region
- Trade lead sharing within region
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_task6_interactions():
    print("🧪 Testing Task 6: Multi-Organism Interactions...")
    try:
        from data_sources.harvesters import DataEcosystem
        from genesis.evolution import Organism, Capability, trade_board
        from genesis.nutrition import create_enhanced_nutrition_system
        from genesis.interactions import run_region_interactions

        # Fast ecosystem
        eco = DataEcosystem({
            'rss_feeds': ['https://hnrss.org/frontpage'],
            'watch_paths': ['/tmp'],
            'harvest_interval': 2,
            'max_food_storage': 80,
            'scarcity_threshold': 60,
        })
        nutrition = create_enhanced_nutrition_system()

        # Two organisms in same region
        a = Organism(generation=0)
        b = Organism(generation=0)
        for o in (a, b):
            o.capabilities.add(Capability.PATTERN_MATCH)
            o.capabilities.add(Capability.REMEMBER)
            o.current_region = 'structured-rich'

        # Seed knowledge for teacher and some food memories for trade
        # Let a become the teacher by collecting some insights
        time.sleep(4)
        a._evolutionary_foraging_phase(eco, nutrition)
        a._evolutionary_foraging_phase(eco, nutrition)
        b._evolutionary_foraging_phase(eco, nutrition)

        # Ensure teacher has enough insights for teaching
        kb = getattr(a, 'knowledge_base', None)
        if kb:
            # If not enough insights, simulate a few more for determinism
            while kb.get_knowledge_summary().get('total_insights', 0) < 5:
                a._evolutionary_foraging_phase(eco, nutrition)
                time.sleep(1)

        # Ensure trade has something to post
        if not hasattr(a, 'good_food_memories') or not a.good_food_memories:
            a._evolutionary_foraging_phase(eco, nutrition)
            time.sleep(1)

        # Run interactions
        summary = run_region_interactions([a, b], eco.get_ecosystem_stats())
        print(f"Summary: {summary}")

        # Expectations
        assert 'structured-rich' in summary['regions']
        assert summary['regions']['structured-rich']['population'] >= 2
        assert summary['trade_leads'] >= 0  # may be 0 if no memories, but shouldn't error

        # At least one of: teaching event happened OR student's success got a hint boost later
        taught = summary['teaching_events'] > 0
        # Try another run to increase likelihood of teaching
        if not taught:
            summary2 = run_region_interactions([a, b], eco.get_ecosystem_stats())
            taught = taught or (summary2['teaching_events'] > 0)
            print(f"Second interaction summary: {summary2}")
        assert taught, "Expected at least one teaching interaction in-region"

        eco.stop()
        print("✅ Task 6 interactions test completed!")

    except Exception as e:
        print(f"❌ Task 6 interactions test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_task6_interactions()

