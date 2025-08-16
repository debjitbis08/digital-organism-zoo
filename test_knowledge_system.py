#!/usr/bin/env python3
"""
Test the real knowledge extraction and teaching system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_knowledge_extraction():
    print("🧠 Testing Real Knowledge Extraction and Teaching...")
    
    try:
        # Import required modules
        from data_sources.harvesters import DataMorsel, DataType
        from genesis.evolution import Organism, Capability
        from genesis.nutrition import create_enhanced_nutrition_system
        from genesis.llm_teacher import create_llm_teacher_system
        import time
        
        # Create test organism with advanced capabilities
        print("🦠 Creating test organism...")
        organism = Organism(generation=0)
        organism.capabilities.add(Capability.PATTERN_MATCH)
        organism.capabilities.add(Capability.ABSTRACT)
        organism.capabilities.add(Capability.REMEMBER)
        organism.energy = 50  # Medium energy to test teaching
        organism.age = 75  # Old enough for advanced teaching
        
        # Create nutrition system
        nutrition_system = create_enhanced_nutrition_system()
        
        # Create LLM teacher
        llm_teacher = create_llm_teacher_system()
        
        print(f"Initial organism: Energy={organism.energy}, Age={organism.age}, Caps={len(organism.capabilities)}")
        
        # Create test data morsels with real content
        test_data = [
            DataMorsel(
                data_type=DataType.XML_DATA,
                content="Title: Revolutionary AI breakthrough in machine learning efficiency\nSummary: Researchers at Stanford develop new algorithm that reduces neural network training time by 60% using quantum-inspired optimization techniques. The breakthrough could accelerate AI development across multiple industries.",
                size=200,
                source="RSS:Tech News",
                timestamp=time.time(),
                energy_value=15
            ),
            DataMorsel(
                data_type=DataType.CODE,
                content="def optimize_neural_network(layers, data):\n    # Quantum-inspired optimization algorithm\n    import numpy as np\n    import tensorflow as tf\n    \n    for layer in layers:\n        # Apply quantum gate transformations\n        layer.weights = quantum_optimize(layer.weights)\n    return layers",
                size=150,
                source="File:optimization.py",
                timestamp=time.time(),
                energy_value=25
            ),
            DataMorsel(
                data_type=DataType.STRUCTURED_JSON,
                content='{"api_response": {"status": "success", "data": {"trending_topics": ["AI", "quantum computing", "neural networks"], "popularity_score": 0.95, "category": "technology"}}}',
                size=120,
                source="API:TrendingTopics",
                timestamp=time.time(),
                energy_value=18
            )
        ]
        
        # Test knowledge extraction from each data type
        print("\n🍽️  Testing knowledge extraction...")
        for i, data_morsel in enumerate(test_data, 1):
            print(f"\n--- Test {i}: {data_morsel.data_type.value} ---")
            print(f"Content preview: {data_morsel.content[:60]}...")
            
            # Process the food (this should extract knowledge)
            organism._process_found_food(data_morsel, nutrition_system)
            
            # Check if knowledge was extracted
            if hasattr(organism, 'knowledge_base'):
                summary = organism.knowledge_base.get_knowledge_summary()
                print(f"Knowledge extracted: {summary['total_insights']} insights")
                print(f"Expertise areas: {summary['expertise_areas']}")
                print(f"Learning activity: {summary['learning_activity']}")
                
                # Show recent knowledge
                if hasattr(organism.knowledge_base, 'knowledge_items') and organism.knowledge_base.knowledge_items:
                    recent = organism.knowledge_base.knowledge_items[-3:]
                    print("Recent insights:")
                    for insight in recent:
                        print(f"  - {insight.insight_type.value}: {insight.content}")
            else:
                print("❌ No knowledge base created!")
        
        # Test teaching with real knowledge
        print("\n🧠 Testing LLM Teaching with Real Knowledge...")
        if hasattr(organism, 'knowledge_base'):
            # Test different teaching scenarios
            teaching_scenarios = [
                ("energy_help", {"reason": "Organism struggling with low energy"}),
                ("capability_guidance", {"reason": "Organism wants to learn new skills"}),
                ("general_advice", {"reason": "Organism asking for wisdom about AI trends"})
            ]
            
            for request_type, context in teaching_scenarios:
                print(f"\nTeaching scenario: {request_type}")
                response = llm_teacher.provide_intelligent_guidance(organism, request_type, context)
                print(f"Teaching mode: {response.teaching_mode.value}")
                print(f"Advice: \"{response.advice}\"")
                print(f"Confidence: {response.confidence}")
                if response.code_modification_hint:
                    print(f"Code hint: {response.code_modification_hint}")
        
        # Final knowledge summary
        print("\n📊 Final Knowledge Summary:")
        if hasattr(organism, 'knowledge_base'):
            final_summary = organism.knowledge_base.get_knowledge_summary()
            print(f"Total insights: {final_summary['total_insights']}")
            print(f"Expertise areas: {final_summary['expertise_areas']}")
            print(f"Problem-solving capable: {final_summary['problem_solving_capable']}")
            print(f"Learning activity: {final_summary['learning_activity']}")
            
            # Test insight generation
            insight = organism.knowledge_base.generate_insight()
            if insight:
                print(f"Generated insight: {insight}")
            
        print("\n✅ Knowledge extraction and teaching test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_knowledge_extraction()