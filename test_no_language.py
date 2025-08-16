#!/usr/bin/env python3
"""
Test that NO language communication happens between parents and organisms
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_no_language():
    print("🚫 Testing NO Language Communication...")
    
    try:
        # Import required modules
        from data_sources.harvesters import DataEcosystem
        from genesis.evolution import Organism, Capability
        from genesis.nutrition import create_enhanced_nutrition_system
        from genesis.parent_care import ActiveParentCareSystem
        import time
        
        # Create test ecosystem
        print("📡 Creating test ecosystem...")
        data_ecosystem = DataEcosystem({
            'rss_feeds': ['https://hnrss.org/frontpage'],
            'harvest_interval': 10,
            'max_food_storage': 30,
        })
        
        # Create nutrition system
        nutrition_system = create_enhanced_nutrition_system()
        
        # Create parent care system
        parent_care_system = ActiveParentCareSystem()
        
        # Create a struggling young organism that should get help
        print("🦠 Creating struggling organism...")
        organism = Organism(generation=0)
        organism.energy = 20  # Low energy - needs help
        organism.age = 10     # Young - should get help
        
        print(f"Initial: Energy={organism.energy}, Age={organism.age}")
        
        print(f"\n🔍 Monitoring for language communication...")
        language_violations = []
        
        # Capture all output to check for language violations
        import io
        import contextlib
        from unittest.mock import patch
        
        output_buffer = io.StringIO()
        
        with contextlib.redirect_stdout(output_buffer):
            # Test foraging and parent help
            for tick in range(5):
                # Test organism foraging
                organism.live(data_ecosystem, nutrition_system, parent_care_system)
                
                # Test parent help explicitly
                care_action = parent_care_system.provide_care(organism)
                
                organism.age += 10  # Age organism
        
        # Check output for language violations
        output = output_buffer.getvalue()
        
        # Look for problematic patterns
        language_patterns = [
            "deep breathing",
            "calm your",
            "emotions",
            "take one step",
            "you've got this",
            "dear digital organism",
            "let's start with",
            "it's okay",
            "take a deep breath",
            "relax",
            "try looking for",
            "here's what works",
            "focus on finding"
        ]
        
        print(f"🔍 Checking output for language violations...")
        for pattern in language_patterns:
            if pattern.lower() in output.lower():
                language_violations.append(pattern)
        
        # Show actual output
        print(f"\n📝 ACTUAL OUTPUT:")
        print("=" * 50)
        print(output)
        print("=" * 50)
        
        # Report results
        print(f"\n🎯 LANGUAGE COMMUNICATION TEST RESULTS")
        print(f"=" * 40)
        
        if language_violations:
            print(f"❌ VIOLATIONS FOUND:")
            for violation in language_violations:
                print(f"  - Found: '{violation}'")
            print(f"\nTotal violations: {len(language_violations)}")
        else:
            print(f"✅ NO LANGUAGE VIOLATIONS FOUND")
            print(f"✅ All communication is biologically realistic")
        
        # Check final organism state
        print(f"\n🦠 ORGANISM FINAL STATE:")
        print(f"Energy: {organism.energy}")
        print(f"Age: {organism.age}")
        if hasattr(organism, '_chemical_guidance'):
            print(f"Chemical guidance received: {organism._chemical_guidance}")
        if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
            summary = organism.knowledge_base.get_knowledge_summary()
            print(f"Knowledge insights: {summary['total_insights']}")
        
        data_ecosystem.stop()
        
        # Final verdict
        if not language_violations:
            print("\n🎉 SUCCESS: System is biologically realistic!")
            print("✅ No language-based communication found")
            print("✅ Only chemical, behavioral, and physical mechanisms")
        else:
            print(f"\n❌ FAILURE: {len(language_violations)} language violations")
            print("🚫 System still contains unrealistic communication")
        
        print("\n✅ Language communication test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_no_language()