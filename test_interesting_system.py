#!/usr/bin/env python3
"""
Test the improved system with visible insights and communication
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_interesting_system():
    print("🎉 Testing Improved Digital Organism System...")
    
    try:
        # Import required modules
        from data_sources.harvesters import DataEcosystem
        from genesis.evolution import Organism, Capability
        from genesis.nutrition import create_enhanced_nutrition_system
        from genesis.parent_care import ActiveParentCareSystem
        import time
        
        # Create test ecosystem with more food
        print("📡 Creating abundant data ecosystem...")
        data_ecosystem = DataEcosystem({
            'rss_feeds': ['https://hnrss.org/frontpage'],
            'harvest_interval': 5,    # Very fast harvesting
            'max_food_storage': 200,
            'scarcity_threshold': 100
        })
        
        # Create nutrition system
        nutrition_system = create_enhanced_nutrition_system()
        
        # Create parent care system
        parent_care_system = ActiveParentCareSystem()
        
        # Create organisms
        print("🦠 Creating test organisms...")
        organisms = []
        for i in range(3):
            organism = Organism(generation=0)
            organism.energy = 50 + (i * 20)  # Different energy levels
            organism.age = i * 20  # Different ages
            organisms.append(organism)
            print(f"Organism {i+1}: Energy={organism.energy}, Age={organism.age}")
        
        # Wait for food to be available
        print("\n⏳ Waiting for food to be harvested...")
        time.sleep(8)
        
        # Check ecosystem status
        eco_stats = data_ecosystem.get_ecosystem_stats()
        print(f"Ecosystem: {eco_stats['total_food_available']} food available")
        
        print(f"\n🎬 Running interesting organism simulation...")
        
        for cycle in range(10):
            print(f"\n--- Cycle {cycle + 1} ---")
            
            # Process all organisms
            for i, organism in enumerate(organisms):
                print(f"\nOrganism {i+1} (Energy: {organism.energy:.1f}, Age: {organism.age}):")
                
                # Let organism live (forage, learn, communicate)
                initial_energy = organism.energy
                organism.live(data_ecosystem, nutrition_system, parent_care_system)
                
                energy_change = organism.energy - initial_energy
                if energy_change > 0:
                    print(f"  ✅ Energy gained: +{energy_change:.1f}")
                elif energy_change < 0:
                    print(f"  ⚡ Energy lost: {energy_change:.1f}")
                
                # Show knowledge status
                if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
                    summary = organism.knowledge_base.get_knowledge_summary()
                    if summary['total_insights'] > 0:
                        print(f"  🧠 Knowledge: {summary['total_insights']} insights, Activity: {summary['learning_activity']}")
                        if summary['expertise_areas']:
                            print(f"      Expertise: {summary['expertise_areas']}")
                
                # Age organism
                organism.age += 5
            
            # Show ecosystem status every few cycles
            if cycle % 3 == 0:
                eco_stats = data_ecosystem.get_ecosystem_stats()
                print(f"\n🌍 Ecosystem: {eco_stats['total_food_available']} food, Scarcity: {eco_stats['food_scarcity']:.2f}")
            
            time.sleep(1)  # Pause between cycles
        
        # Final summary
        print(f"\n📊 FINAL ORGANISM STATUS")
        print(f"=" * 40)
        
        for i, organism in enumerate(organisms):
            print(f"\nOrganism {i+1}:")
            print(f"  Energy: {organism.energy:.1f}")
            print(f"  Age: {organism.age}")
            print(f"  Capabilities: {len(organism.capabilities)}")
            
            if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
                summary = organism.knowledge_base.get_knowledge_summary()
                print(f"  Total insights: {summary['total_insights']}")
                print(f"  Learning activity: {summary['learning_activity']}")
                if summary['expertise_areas']:
                    print(f"  Expertise areas: {summary['expertise_areas']}")
                
                # Show recent insights
                if hasattr(organism.knowledge_base, 'knowledge_items') and organism.knowledge_base.knowledge_items:
                    recent_insights = organism.knowledge_base.knowledge_items[-3:]
                    print(f"  Recent insights:")
                    for insight in recent_insights:
                        print(f"    - {insight.content}")
            
            # Show behavioral changes
            if hasattr(organism, '_behavior_modifiers'):
                significant_changes = {k: v for k, v in organism._behavior_modifiers.items() 
                                     if isinstance(v, float) and v > 0.05}
                if significant_changes:
                    print(f"  Behavioral changes: {significant_changes}")
        
        # Test communication explicitly
        print(f"\n📡 TESTING ORGANISM COMMUNICATION")
        print(f"=" * 40)
        print("Forcing communication attempts...")
        
        for organism in organisms:
            if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
                summary = organism.knowledge_base.get_knowledge_summary()
                if summary['total_insights'] >= 1:
                    # Force communication by setting high energy and calling method
                    temp_energy = organism.energy
                    organism.energy = 90  # High energy for success signal
                    organism.communicate_with_other_organisms()
                    organism.energy = temp_energy
        
        data_ecosystem.stop()
        print("\n✅ Interesting system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_interesting_system()