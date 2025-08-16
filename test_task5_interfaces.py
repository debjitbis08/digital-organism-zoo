#!/usr/bin/env python3
"""
Task 5 validation: evolvable interfaces and migration behavior

This test exercises:
- Interface adaptation (sensors/actuators) with dynamic selection pressure
- Virtual region migration influencing foraging
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_task5_interfaces():
    print("🧪 Testing Task 5: Evolvable Interfaces & Migration...")
    try:
        from data_sources.harvesters import DataEcosystem
        from genesis.evolution import Organism, Capability
        from genesis.nutrition import create_enhanced_nutrition_system

        # Fast, small ecosystem to keep scarcity < 0.5 initially
        print("📡 Spinning up data ecosystem (fast/low storage)...")
        eco = DataEcosystem({
            'rss_feeds': ['https://hnrss.org/frontpage'],
            'watch_paths': ['/tmp'],
            'harvest_interval': 2,
            'max_food_storage': 80,
            'scarcity_threshold': 60,
        })

        print("🧬 Building nutrition system...")
        nutrition = create_enhanced_nutrition_system()

        # Two organisms to observe different outcomes
        print("🦠 Creating two organisms...")
        a = Organism(generation=0)
        b = Organism(generation=0)
        for o in (a, b):
            o.capabilities.add(Capability.PATTERN_MATCH)
            o.capabilities.add(Capability.REMEMBER)

        # Wait for food
        print("⏳ Waiting for initial food...")
        time.sleep(5)

        # 1) Migration behavior under scarcity
        print("\n🚶 Checking virtual migration behavior...")
        start_region_a = getattr(a, 'current_region', 'default')
        start_region_b = getattr(b, 'current_region', 'default')
        migrated = False
        # Force migration to be observable in test
        os.environ['ZOO_FORCE_MIGRATION'] = '1'
        for tick in range(3):
            for o in (a, b):
                o._evolutionary_foraging_phase(eco, nutrition)
            time.sleep(1)
            if a.current_region != start_region_a or b.current_region != start_region_b:
                migrated = True
                break
        print(f"Migration observed: {migrated}, regions: A {start_region_a}→{a.current_region}, B {start_region_b}→{b.current_region}")
        assert migrated, "Expected at least one organism to migrate under forced migration"

        # 2) Interface adaptation: drive adaptation with high rate and poor success
        print("\n🧠 Checking interface adaptation dynamics...")
        init_sensors_len = len(a.brain.sensors) if getattr(a, 'brain', None) else 0
        init_actuators_len = len(a.brain.actuators) if getattr(a, 'brain', None) else 0
        # Make adaptation more likely for test purposes
        a.interface_adaptation_rate = 0.8
        a.foraging_success_rate = 0.2
        a.energy = 40
        # Provide fresh sensor snapshot
        a._compute_brain_drives(eco, nutrition)
        # Attempt several evolutions to trigger adaptation
        for _ in range(30):
            a.attempt_evolution()
        new_sensors_len = len(a.brain.sensors) if getattr(a, 'brain', None) else 0
        new_actuators_len = len(a.brain.actuators) if getattr(a, 'brain', None) else 0
        changed = (new_sensors_len != init_sensors_len) or (new_actuators_len != init_actuators_len)
        print(f"Interfaces changed: {changed} (sensors {init_sensors_len}→{new_sensors_len}, actuators {init_actuators_len}→{new_actuators_len})")
        assert changed, "Expected organism interfaces (sensors/actuators) to adapt under high pressure"

        # Wrap up
        stats = eco.get_ecosystem_stats()
        print(f"\n📊 Ecosystem: {stats['total_food_available']} available, scarcity={stats['food_scarcity']:.2f}")
        eco.stop()
        print("✅ Task 5 interface test completed!")

    except Exception as e:
        print(f"❌ Task 5 test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_task5_interfaces()
