#!/usr/bin/env python3
"""
Test the fixed system with improved capabilities and reduced emergency food
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fixed_system():
    print("🔧 Testing Fixed Digital Organism System...")
    
    try:
        # Import required modules
        from data_sources.harvesters import DataEcosystem
        from genesis.evolution import Organism, Capability
        from genesis.nutrition import create_enhanced_nutrition_system
        from genesis.community_activities import create_community_system, check_community_activities
        import time
        
        # Create test ecosystem with real data sources
        print("📡 Creating real data ecosystem...")
        data_ecosystem = DataEcosystem({
            'rss_feeds': ['https://hnrss.org/frontpage'],
            'watch_paths': ['/tmp'],
            'harvest_interval': 5,    # Very fast harvesting for testing
            'max_food_storage': 100,
            'scarcity_threshold': 30
        })
        
        # Create nutrition system
        print("🧬 Creating nutrition system...")
        nutrition_system = create_enhanced_nutrition_system()
        
        # Create community system
        print("🏘️  Creating community system...")
        community_system = create_community_system()
        
        # Create test organisms with improved capabilities
        print("🦠 Creating test organisms with fixed capabilities...")
        organisms = []
        for i in range(3):
            organism = Organism(generation=0)
            print(f"Organism {organism.id}: Energy={organism.energy}, Caps={list(c.value for c in organism.capabilities)}")
            organisms.append(organism)
        
        # Wait for real food to be harvested
        print("⏳ Waiting for real food to be harvested...")
        time.sleep(8)
        
        # Check ecosystem status
        eco_stats = data_ecosystem.get_ecosystem_stats()
        print(f"Ecosystem: {eco_stats['total_food_available']} food available")
        print(f"Food types: {eco_stats['food_by_type']}")
        
        print(f"\n🍽️  Testing feeding with improved organisms...")
        successful_feeds = 0
        emergency_feeds = 0
        
        # Test multiple feeding cycles
        for cycle in range(10):
            print(f"\n--- Feeding Cycle {cycle + 1} ---")
            
            for i, organism in enumerate(organisms):
                print(f"Organism {i+1} (Energy: {organism.energy:.1f}):")
                
                # Test foraging
                initial_energy = organism.energy
                organism._evolutionary_foraging_phase(data_ecosystem, nutrition_system)
                
                energy_gained = organism.energy - initial_energy
                if energy_gained > 0:
                    # Check what type of food was consumed
                    if hasattr(organism, 'good_food_memories') and organism.good_food_memories:
                        recent_food = organism.good_food_memories[-1]
                        if 'Emergency_Generator' in recent_food:
                            emergency_feeds += 1
                            print(f"  ❌ Ate emergency food (+{energy_gained:.1f} energy)")
                        else:
                            successful_feeds += 1
                            print(f"  ✅ Ate real data (+{energy_gained:.1f} energy)")
                    else:
                        successful_feeds += 1
                        print(f"  ✅ Gained energy (+{energy_gained:.1f})")
                else:
                    print(f"  😋 No food found")
                
                # Show knowledge accumulation
                if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
                    summary = organism.knowledge_base.get_knowledge_summary()
                    if summary['total_insights'] > 0:
                        print(f"  🧠 Knowledge: {summary['total_insights']} insights, Activity: {summary['learning_activity']}")
            
            # Check for community activities
            if len(organisms) > 1:
                print(f"\n🏘️  Checking community activities...")
                eco_stats = data_ecosystem.get_ecosystem_stats()
                activities = check_community_activities(organisms, eco_stats, community_system)
                
                if activities:
                    print(f"  🎯 {len(activities)} community activities occurred!")
                else:
                    print(f"  📊 No community activities this cycle")
            
            time.sleep(2)  # Brief pause between cycles
        
        # Final analysis
        print(f"\n📊 FEEDING ANALYSIS")
        print(f"=" * 30)
        print(f"Real data feeds: {successful_feeds}")
        print(f"Emergency feeds: {emergency_feeds}")
        print(f"Success rate: {successful_feeds/(successful_feeds + emergency_feeds)*100:.1f}%" if (successful_feeds + emergency_feeds) > 0 else "No feeding occurred")
        
        # Show final organism states
        print(f"\n🦠 FINAL ORGANISM STATES")
        print(f"=" * 30)
        for i, organism in enumerate(organisms):
            print(f"Organism {i+1} ({organism.id}):")
            print(f"  Energy: {organism.energy:.1f}")
            print(f"  Age: {organism.age}")
            print(f"  Capabilities: {len(organism.capabilities)}")
            if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
                summary = organism.knowledge_base.get_knowledge_summary()
                print(f"  Knowledge: {summary['total_insights']} insights")
                if summary['expertise_areas']:
                    print(f"  Expertise: {summary['expertise_areas']}")
            if hasattr(organism, '_behavior_modifiers'):
                significant_mods = {k: v for k, v in organism._behavior_modifiers.items() 
                                   if isinstance(v, float) and v > 0.1}
                if significant_mods:
                    print(f"  Behaviors: {significant_mods}")
        
        # Community stats
        community_stats = community_system.get_community_stats()
        if community_stats['total_activities'] > 0:
            print(f"\n🏘️  COMMUNITY ACCOMPLISHMENTS")
            print(f"=" * 30)
            print(f"Total activities: {community_stats['total_activities']}")
            print(f"Activity types: {community_stats['activity_types']}")
            print(f"Total impact: {community_stats['total_impact']:.1f}")
            print(f"Community benefit: {community_stats['community_benefit']:.1f}")
        
        data_ecosystem.stop()
        
        # Verdict
        if successful_feeds > emergency_feeds:
            print("\n✅ SUCCESS: Organisms primarily consuming real internet data!")
        elif successful_feeds > 0:
            print("\n⚠️  PARTIAL SUCCESS: Some real data consumption, but still emergency dependency")
        else:
            print("\n❌ ISSUE: Organisms still relying entirely on emergency food")
        
        print("\n✅ Fixed system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_system()