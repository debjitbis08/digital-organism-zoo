#!/usr/bin/env python3
"""
Test the new evolutionary foraging system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_foraging():
    print("🧪 Testing Evolutionary Foraging System...")
    
    try:
        # Import required modules
        from data_sources.harvesters import DataEcosystem
        from genesis.evolution import Organism, Capability
        from genesis.nutrition import create_enhanced_nutrition_system
        
        # Create test ecosystem with faster harvesting
        print("📡 Creating test data ecosystem...")
        data_ecosystem = DataEcosystem({
            'rss_feeds': ['https://hnrss.org/frontpage'],
            'watch_paths': ['/tmp'],
            'harvest_interval': 2,    # Very fast harvesting
            'max_food_storage': 100,
            'scarcity_threshold': 50
        })
        
        # Create nutrition system
        print("🧬 Creating nutrition system...")
        nutrition_system = create_enhanced_nutrition_system()
        
        # Create test organism
        print("🦠 Creating test organism...")
        organism = Organism(generation=0)
        organism.capabilities.add(Capability.PATTERN_MATCH)
        organism.capabilities.add(Capability.REMEMBER)
        
        print(f"Initial organism: Energy={organism.energy}, Caps={len(organism.capabilities)}")
        
        # Wait for some food to be harvested
        print("⏳ Waiting for food to be harvested...")
        import time
        time.sleep(5)
        
        # Check ecosystem status
        eco_stats = data_ecosystem.get_ecosystem_stats()
        print(f"Ecosystem: {eco_stats['total_food_available']} food available")
        print(f"Food types: {eco_stats['food_by_type']}")
        
        # Test foraging
        print("\n🍽️  Testing evolutionary foraging...")
        for tick in range(5):
            print(f"\n--- Tick {tick + 1} ---")
            print(f"Before: Energy={organism.energy:.1f}")
            
            # Test the foraging phase
            organism._evolutionary_foraging_phase(data_ecosystem, nutrition_system)
            
            print(f"After: Energy={organism.energy:.1f}")
            
            # Check foraging success rate
            if hasattr(organism, 'foraging_success_rate'):
                print(f"Foraging success rate: {organism.foraging_success_rate:.2f}")
            
            # Check food memories
            if hasattr(organism, 'good_food_memories'):
                print(f"Food memories: {len(organism.good_food_memories)}")
            
            time.sleep(2)  # Wait for more food
        
        # Final stats
        final_stats = data_ecosystem.get_ecosystem_stats()
        print(f"\n📊 Final Stats:")
        print(f"Food available: {final_stats['total_food_available']}")
        print(f"Food consumed: {final_stats['total_food_consumed']}")
        print(f"Organism energy: {organism.energy:.1f}")
        print(f"Organism age: {organism.age}")
        
        data_ecosystem.stop()
        print("✅ Foraging test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_foraging()