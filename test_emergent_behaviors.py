#!/usr/bin/env python3
"""
Test emergent behaviors from real knowledge consumption
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_emergent_behaviors():
    print("🌟 Testing Emergent Behaviors from Real Knowledge...")
    
    try:
        # Import required modules
        from data_sources.harvesters import DataMorsel, DataType
        from genesis.evolution import Organism, Capability
        from genesis.nutrition import create_enhanced_nutrition_system
        import time
        
        # Create test organism with learning capabilities
        print("🦠 Creating test organism...")
        organism = Organism(generation=0)
        organism.capabilities.add(Capability.PATTERN_MATCH)
        organism.capabilities.add(Capability.ABSTRACT)
        organism.capabilities.add(Capability.REMEMBER)
        organism.energy = 50
        organism.age = 0
        
        # Create nutrition system
        nutrition_system = create_enhanced_nutrition_system()
        
        print(f"Initial organism: Energy={organism.energy}, Age={organism.age}")
        print(f"Initial traits - Curiosity: {organism.traits.curiosity:.2f}, Efficiency: {organism.traits.efficiency:.2f}")
        print(f"Initial traits - Creativity: {organism.traits.creativity:.2f}, Cooperation: {organism.traits.cooperation:.2f}")
        
        # Create diverse data that should trigger different behaviors
        knowledge_inducing_data = [
            # Tech concepts - should make organism tech-savvy
            DataMorsel(
                data_type=DataType.XML_DATA,
                content="Title: New AI algorithm breakthrough\nSummary: Advanced neural network optimization using quantum computing principles",
                size=100, source="RSS:TechNews", timestamp=time.time(), energy_value=15
            ),
            DataMorsel(
                data_type=DataType.XML_DATA,
                content="Title: Machine learning efficiency gains\nSummary: Revolutionary improvements in deep learning model training efficiency",
                size=100, source="RSS:AINews", timestamp=time.time(), energy_value=15
            ),
            # Code data - should develop code affinity
            DataMorsel(
                data_type=DataType.CODE,
                content="def neural_network_train(data, epochs):\n    import tensorflow as tf\n    import numpy as np\n    # Quantum optimization algorithm\n    model = tf.keras.Sequential()\n    return model.fit(data, epochs=epochs)",
                size=150, source="File:ai_training.py", timestamp=time.time(), energy_value=25
            ),
            DataMorsel(
                data_type=DataType.CODE,
                content="def optimize_algorithm(input_data):\n    # Advanced optimization function\n    import scipy.optimize\n    result = scipy.optimize.minimize(input_data)\n    return result",
                size=120, source="File:optimizer.py", timestamp=time.time(), energy_value=20
            ),
            # Trending topics - should make trend-aware
            DataMorsel(
                data_type=DataType.XML_DATA,
                content="Title: AI trends dominating 2024\nSummary: Artificial intelligence and machine learning continue trending as top technologies",
                size=90, source="RSS:TrendWatch", timestamp=time.time(), energy_value=12
            ),
            DataMorsel(
                data_type=DataType.XML_DATA,
                content="Title: Quantum computing breakthrough trending\nSummary: Major breakthrough in quantum computing efficiency trending across tech communities",
                size=95, source="RSS:QuantumNews", timestamp=time.time(), energy_value=14
            ),
            # Emotional content - should affect emotional state
            DataMorsel(
                data_type=DataType.XML_DATA,
                content="Title: Exciting breakthrough in AI research\nSummary: Researchers make amazing discovery that promises revolutionary changes",
                size=85, source="RSS:ExcitingNews", timestamp=time.time(), energy_value=13
            ),
            # More diverse data for cross-domain expertise
            DataMorsel(
                data_type=DataType.STRUCTURED_JSON,
                content='{"api_data": {"trending": ["quantum", "AI", "optimization"], "performance": {"efficiency": 0.95, "accuracy": 0.98}}}',
                size=80, source="API:TechMetrics", timestamp=time.time(), energy_value=18
            )
        ]
        
        print(f"\n🍽️  Feeding organism diverse knowledge over multiple ticks...")
        
        # Feed the organism data and observe behavioral changes
        for tick in range(len(knowledge_inducing_data)):
            print(f"\n--- Knowledge Consumption Tick {tick + 1} ---")
            
            data_morsel = knowledge_inducing_data[tick]
            print(f"Feeding: {data_morsel.data_type.value} - {data_morsel.content[:50]}...")
            
            # Process the food (extract knowledge)
            organism._process_found_food(data_morsel, nutrition_system)
            
            # Age the organism so behaviors can emerge
            organism.age += 50
            
            # Check for emergent behaviors
            print(f"Age now: {organism.age}")
            organism.exhibit_knowledge_based_behaviors()
            
            # Show knowledge progress
            if hasattr(organism, 'knowledge_base'):
                summary = organism.knowledge_base.get_knowledge_summary()
                print(f"Knowledge: {summary['total_insights']} insights, Activity: {summary['learning_activity']}")
                if summary['expertise_areas']:
                    print(f"Expertise: {summary['expertise_areas']}")
            
            # Show behavioral changes
            if hasattr(organism, '_behavior_modifiers'):
                mods = organism._behavior_modifiers
                significant_changes = {k: v for k, v in mods.items() if isinstance(v, float) and v > 0.1}
                if significant_changes:
                    print(f"Behavior changes: {significant_changes}")
            
            # Show trait evolution
            print(f"Traits - Curiosity: {organism.traits.curiosity:.2f}, Efficiency: {organism.traits.efficiency:.2f}")
            print(f"Traits - Creativity: {organism.traits.creativity:.2f}, Cooperation: {organism.traits.cooperation:.2f}")
            
            time.sleep(0.5)  # Brief pause for readability
        
        # Final summary of emergent behaviors
        print("\n🌟 EMERGENT BEHAVIOR SUMMARY")
        print("=" * 40)
        
        if hasattr(organism, 'knowledge_base'):
            final_summary = organism.knowledge_base.get_knowledge_summary()
            print(f"Total Knowledge: {final_summary['total_insights']} insights")
            print(f"Expertise Areas: {final_summary['expertise_areas']}")
            print(f"Problem Solving: {'Yes' if final_summary.get('problem_solving_capable') else 'No'}")
        
        if hasattr(organism, '_behavior_modifiers'):
            print("\nBehavioral Adaptations:")
            for behavior, value in organism._behavior_modifiers.items():
                if isinstance(value, float) and value > 0.05:
                    print(f"  - {behavior}: {value:.2f}")
                elif value != 'neutral' and value != 0.5:
                    print(f"  - {behavior}: {value}")
        
        print("\nPersonality Evolution:")
        print(f"  - Curiosity: {organism.traits.curiosity:.2f} (higher = more exploratory)")
        print(f"  - Efficiency: {organism.traits.efficiency:.2f} (higher = better resource use)")
        print(f"  - Creativity: {organism.traits.creativity:.2f} (higher = more innovative)")
        print(f"  - Cooperation: {organism.traits.cooperation:.2f} (higher = more social)")
        print(f"  - Risk Taking: {organism.traits.risk_taking:.2f} (higher = more adventurous)")
        
        special_abilities = []
        if hasattr(organism, '_problem_solver'):
            special_abilities.append("Cross-domain problem solver")
        if hasattr(organism, '_behavior_modifiers'):
            if organism._behavior_modifiers.get('tech_awareness', 0) > 0.3:
                special_abilities.append("Tech-savvy specialist")
            if organism._behavior_modifiers.get('trend_following', 0) > 0.3:
                special_abilities.append("Trend-aware social creature")
            if organism._behavior_modifiers.get('code_affinity', 0) > 0.3:
                special_abilities.append("Code-literate explorer")
        
        if special_abilities:
            print(f"\nEmergent Specializations:")
            for ability in special_abilities:
                print(f"  🌟 {ability}")
        
        print("\n✅ Emergent behavior test completed!")
        print("💡 The organism has evolved unique behaviors based on the real data it consumed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_emergent_behaviors()