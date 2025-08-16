#!/usr/bin/env python3
"""
Debug knowledge extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_knowledge_debug():
    print("🔍 Debugging Knowledge Extraction...")
    
    try:
        from data_sources.harvesters import DataMorsel, DataType
        from genesis.data_processor import create_data_processor
        from genesis.evolution import Capability
        import time
        
        # Create data processor
        processor = create_data_processor()
        
        # Create sample RSS content like what we're getting
        sample_rss = "Title: Is air travel getting worse?\nSummary: <p>Article URL: <a href=\"https://www.example.com\">Read more</a></p> This discusses AI and machine learning algorithms."
        
        data_morsel = DataMorsel(
            data_type=DataType.XML_DATA,
            content=sample_rss,
            size=len(sample_rss),
            source="RSS:Test",
            timestamp=time.time(),
            energy_value=15
        )
        
        # Test with organism capabilities
        organism_capabilities = {Capability.EAT_TEXT, Capability.SENSE_DATA, Capability.PATTERN_MATCH, Capability.MOVE}
        
        print(f"Content: {sample_rss}")
        print(f"Capabilities: {[cap.value for cap in organism_capabilities]}")
        
        # Process the data
        knowledge_extracted = processor.process_real_data(data_morsel, organism_capabilities)
        
        print(f"Extracted: {len(knowledge_extracted)} insights")
        for knowledge in knowledge_extracted:
            print(f"  - {knowledge.insight_type.value}: {knowledge.content}")
        
        # Test with a more obvious pattern
        ai_content = "Title: Revolutionary AI breakthrough in machine learning\nSummary: Scientists develop new artificial intelligence algorithm"
        
        ai_morsel = DataMorsel(
            data_type=DataType.XML_DATA,
            content=ai_content,
            size=len(ai_content),
            source="RSS:AI",
            timestamp=time.time(),
            energy_value=15
        )
        
        print(f"\nAI Content: {ai_content}")
        ai_knowledge = processor.process_real_data(ai_morsel, organism_capabilities)
        print(f"AI Extracted: {len(ai_knowledge)} insights")
        for knowledge in ai_knowledge:
            print(f"  - {knowledge.insight_type.value}: {knowledge.content}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_knowledge_debug()