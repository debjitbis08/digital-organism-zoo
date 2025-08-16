# Real Data Processing System for Digital Organisms
# Organisms actually read, understand, and use internet data they consume

import re
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import feedparser
from collections import Counter

class DataInsight(Enum):
    """Types of insights organisms can extract from real data"""
    TRENDING_TOPIC = "trending_topic"
    TECHNICAL_CONCEPT = "technical_concept"
    PROBLEM_SOLUTION = "problem_solution"
    HUMAN_EMOTION = "human_emotion"
    FACTUAL_INFO = "factual_info"
    TEMPORAL_PATTERN = "temporal_pattern"
    SOCIAL_SIGNAL = "social_signal"

@dataclass
class ProcessedKnowledge:
    """Knowledge extracted from real data"""
    insight_type: DataInsight
    content: str
    confidence: float
    source: str
    extracted_at: float
    keywords: List[str]
    sentiment: str = "neutral"
    usefulness: float = 0.5
    
    def __post_init__(self):
        self.id = hashlib.md5(f"{self.content}{self.source}".encode()).hexdigest()[:8]

class OrganismDataProcessor:
    """Processes real internet data to extract meaningful insights"""
    
    def __init__(self):
        self.processing_patterns = self._load_processing_patterns()
        self.knowledge_cache = {}
        
    def _load_processing_patterns(self) -> Dict[str, Dict]:
        """Patterns for extracting insights from different data types"""
        return {
            'rss_news': {
                'trending_topics': [
                    r'\b(AI|artificial intelligence|machine learning|LLM)\b',
                    r'\b(climate|environment|carbon|emission)\b',
                    r'\b(crypto|bitcoin|blockchain|ethereum)\b',
                    r'\b(election|politics|government|policy)\b',
                    r'\b(startup|funding|investment|IPO)\b',
                    r'\b(travel|tourism|airline|flight)\b',
                    r'\b(health|medical|drug|treatment)\b',
                    r'\b(economy|economic|inflation|market)\b',
                    r'\b(science|research|study|analysis)\b',
                    r'\b(technology|tech|innovation|development)\b'
                ],
                'technical_concepts': [
                    r'\b(algorithm|framework|protocol|API)\b',
                    r'\b(security|vulnerability|breach|hack)\b',
                    r'\b(performance|optimization|efficiency)\b',
                    r'\b(database|cloud|infrastructure|server)\b'
                ],
                'emotions': [
                    r'\b(breakthrough|revolutionary|amazing)\b',
                    r'\b(concerning|worrying|alarming|crisis)\b',
                    r'\b(exciting|promising|hopeful)\b',
                    r'\b(controversial|debate|criticism)\b'
                ]
            },
            'code_files': {
                'patterns': [
                    r'def\s+(\w+)\([^)]*\):',  # Function definitions
                    r'class\s+(\w+)',         # Class definitions
                    r'import\s+(\w+)',        # Imports
                    r'#\s*(.+)',              # Comments
                    r'(\w+)\s*=\s*(.+)'       # Variable assignments
                ],
                'concepts': [
                    r'\b(optimization|efficiency|performance)\b',
                    r'\b(security|authentication|encryption)\b',
                    r'\b(database|storage|persistence)\b',
                    r'\b(network|api|http|request)\b'
                ]
            }
        }
    
    def process_real_data(self, data_morsel, organism_capabilities: Set) -> List[ProcessedKnowledge]:
        """Extract real knowledge from internet data"""
        
        from data_sources.harvesters import DataType
        from genesis.evolution import Capability
        
        knowledge_list = []
        content = data_morsel.content.lower()
        
        # Process based on data type
        if data_morsel.data_type == DataType.XML_DATA:
            # Process RSS/news data
            knowledge_list.extend(self._process_news_data(data_morsel, content, organism_capabilities))
            
        elif data_morsel.data_type == DataType.CODE:
            # Process code files
            knowledge_list.extend(self._process_code_data(data_morsel, content, organism_capabilities))
            
        elif data_morsel.data_type == DataType.STRUCTURED_JSON:
            # Process JSON data
            knowledge_list.extend(self._process_json_data(data_morsel, content, organism_capabilities))
            
        elif data_morsel.data_type == DataType.SIMPLE_TEXT:
            # Process plain text
            knowledge_list.extend(self._process_text_data(data_morsel, content, organism_capabilities))
        
        # Cache knowledge for organism learning
        for knowledge in knowledge_list:
            self.knowledge_cache[knowledge.id] = knowledge
            
        return knowledge_list
    
    def _process_news_data(self, data_morsel, content: str, capabilities: Set) -> List[ProcessedKnowledge]:
        """Extract insights from news/RSS data"""
        
        from genesis.evolution import Capability
        knowledge = []
        
        # Extract trending topics
        if Capability.PATTERN_MATCH in capabilities:
            for topic_pattern in self.processing_patterns['rss_news']['trending_topics']:
                matches = re.findall(topic_pattern, content, re.IGNORECASE)
                if matches:
                    for match in matches[:2]:  # Limit to 2 per pattern
                        knowledge.append(ProcessedKnowledge(
                            insight_type=DataInsight.TRENDING_TOPIC,
                            content=f"Trending: {match.upper()}",
                            confidence=0.8,
                            source=data_morsel.source,
                            extracted_at=time.time(),
                            keywords=[match.lower()],
                            usefulness=0.7
                        ))
        
        # Extract technical concepts
        if Capability.ABSTRACT in capabilities:
            for tech_pattern in self.processing_patterns['rss_news']['technical_concepts']:
                matches = re.findall(tech_pattern, content, re.IGNORECASE)
                if matches:
                    for match in matches[:1]:  # Limit concepts
                        knowledge.append(ProcessedKnowledge(
                            insight_type=DataInsight.TECHNICAL_CONCEPT,
                            content=f"Tech concept: {match}",
                            confidence=0.7,
                            source=data_morsel.source,
                            extracted_at=time.time(),
                            keywords=[match.lower()],
                            usefulness=0.8
                        ))
        
        # Extract emotional sentiment
        for emotion_pattern in self.processing_patterns['rss_news']['emotions']:
            matches = re.findall(emotion_pattern, content, re.IGNORECASE)
            if matches:
                sentiment = "positive" if any(word in emotion_pattern for word in ["amazing", "exciting", "promising"]) else "negative"
                knowledge.append(ProcessedKnowledge(
                    insight_type=DataInsight.HUMAN_EMOTION,
                    content=f"Sentiment: {sentiment} about {matches[0]}",
                    confidence=0.6,
                    source=data_morsel.source,
                    extracted_at=time.time(),
                    keywords=matches[:3],
                    sentiment=sentiment,
                    usefulness=0.4
                ))
                break  # Only one sentiment per article
        
        return knowledge
    
    def _process_code_data(self, data_morsel, content: str, capabilities: Set) -> List[ProcessedKnowledge]:
        """Extract insights from code files"""
        
        from genesis.evolution import Capability
        knowledge = []
        
        if Capability.ABSTRACT in capabilities:
            # Extract function definitions
            functions = re.findall(r'def\s+(\w+)\([^)]*\):', content)
            if functions:
                knowledge.append(ProcessedKnowledge(
                    insight_type=DataInsight.TECHNICAL_CONCEPT,
                    content=f"Code functions: {', '.join(functions[:3])}",
                    confidence=0.9,
                    source=data_morsel.source,
                    extracted_at=time.time(),
                    keywords=functions[:5],
                    usefulness=0.9
                ))
            
            # Extract imports (dependencies)
            imports = re.findall(r'import\s+(\w+)', content)
            if imports:
                knowledge.append(ProcessedKnowledge(
                    insight_type=DataInsight.TECHNICAL_CONCEPT,
                    content=f"Dependencies: {', '.join(set(imports[:3]))}",
                    confidence=0.8,
                    source=data_morsel.source,
                    extracted_at=time.time(),
                    keywords=list(set(imports[:5])),
                    usefulness=0.7
                ))
        
        # Extract comments (human intentions)
        if Capability.PATTERN_MATCH in capabilities:
            comments = re.findall(r'#\s*(.+)', content)
            if comments:
                meaningful_comments = [c.strip() for c in comments if len(c.strip()) > 10][:2]
                if meaningful_comments:
                    knowledge.append(ProcessedKnowledge(
                        insight_type=DataInsight.HUMAN_EMOTION,
                        content=f"Developer intent: {meaningful_comments[0][:50]}...",
                        confidence=0.6,
                        source=data_morsel.source,
                        extracted_at=time.time(),
                        keywords=[],
                        usefulness=0.5
                    ))
        
        return knowledge
    
    def _process_json_data(self, data_morsel, content: str, capabilities: Set) -> List[ProcessedKnowledge]:
        """Extract insights from JSON data"""
        
        from genesis.evolution import Capability
        knowledge = []
        
        try:
            # Try to parse JSON
            data = json.loads(content)
            
            if Capability.PATTERN_MATCH in capabilities:
                # Extract structure information
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    knowledge.append(ProcessedKnowledge(
                        insight_type=DataInsight.FACTUAL_INFO,
                        content=f"Data structure: {', '.join(keys)}",
                        confidence=0.8,
                        source=data_morsel.source,
                        extracted_at=time.time(),
                        keywords=keys,
                        usefulness=0.6
                    ))
                
                # Look for API-like patterns
                if any(key in str(data).lower() for key in ['api', 'endpoint', 'response', 'status']):
                    knowledge.append(ProcessedKnowledge(
                        insight_type=DataInsight.TECHNICAL_CONCEPT,
                        content="API data structure detected",
                        confidence=0.7,
                        source=data_morsel.source,
                        extracted_at=time.time(),
                        keywords=['api', 'data'],
                        usefulness=0.8
                    ))
                    
        except json.JSONDecodeError:
            # If not valid JSON, treat as text
            pass
        
        return knowledge
    
    def _process_text_data(self, data_morsel, content: str, capabilities: Set) -> List[ProcessedKnowledge]:
        """Extract insights from plain text"""
        
        from genesis.evolution import Capability
        knowledge = []
        
        if Capability.PATTERN_MATCH in capabilities:
            # Extract key phrases
            words = re.findall(r'\b\w{4,}\b', content.lower())
            if words:
                word_freq = Counter(words).most_common(3)
                keywords = [word for word, count in word_freq if count > 1]
                
                if keywords:
                    knowledge.append(ProcessedKnowledge(
                        insight_type=DataInsight.FACTUAL_INFO,
                        content=f"Key concepts: {', '.join(keywords)}",
                        confidence=0.5,
                        source=data_morsel.source,
                        extracted_at=time.time(),
                        keywords=keywords,
                        usefulness=0.4
                    ))
        
        return knowledge

class OrganismKnowledgeBase:
    """Manages an organism's accumulated knowledge from real data"""
    
    def __init__(self):
        self.knowledge_items: List[ProcessedKnowledge] = []
        self.topic_expertise: Dict[str, float] = {}
        self.learning_history: List[Dict] = []
        self.insights_generated: int = 0
        
    def add_knowledge(self, knowledge_list: List[ProcessedKnowledge], organism_id: str):
        """Add new knowledge to organism's knowledge base"""
        
        for knowledge in knowledge_list:
            self.knowledge_items.append(knowledge)
            self.insights_generated += 1
            
            # Build expertise in topics
            for keyword in knowledge.keywords:
                if keyword not in self.topic_expertise:
                    self.topic_expertise[keyword] = 0.0
                self.topic_expertise[keyword] += knowledge.usefulness * 0.1
            
            # Track learning
            self.learning_history.append({
                'timestamp': time.time(),
                'insight': knowledge.insight_type.value,
                'source': knowledge.source,
                'organism': organism_id
            })
            
            print(f"🧠 Organism {organism_id} learned: {knowledge.content}")
        
        # Limit knowledge base size
        if len(self.knowledge_items) > 50:
            # Keep the most useful knowledge
            self.knowledge_items.sort(key=lambda k: k.usefulness, reverse=True)
            self.knowledge_items = self.knowledge_items[:50]
    
    def get_expertise_level(self, topic: str) -> float:
        """Get organism's expertise in a topic"""
        return self.topic_expertise.get(topic.lower(), 0.0)
    
    def can_solve_problem(self, problem_keywords: List[str]) -> bool:
        """Check if organism has knowledge to solve a problem"""
        
        expertise_score = 0.0
        for keyword in problem_keywords:
            expertise_score += self.get_expertise_level(keyword)
        
        return expertise_score > 1.0  # Threshold for problem-solving
    
    def generate_insight(self) -> Optional[str]:
        """Generate new insights by combining existing knowledge"""
        
        if len(self.knowledge_items) < 3:
            return None
        
        # Find patterns across different knowledge items
        recent_knowledge = self.knowledge_items[-10:]
        topics = {}
        
        for knowledge in recent_knowledge:
            for keyword in knowledge.keywords:
                if keyword not in topics:
                    topics[keyword] = []
                topics[keyword].append(knowledge)
        
        # Find connections
        for topic, knowledge_list in topics.items():
            if len(knowledge_list) >= 2:
                sources = list(set([k.source for k in knowledge_list]))
                if len(sources) > 1:
                    return f"Connected {topic} across {', '.join(sources[:2])}"
        
        return None
    
    def get_knowledge_summary(self) -> Dict:
        """Get summary of organism's knowledge"""
        
        if not self.knowledge_items:
            return {"total_insights": 0, "expertise_areas": [], "learning_activity": "none"}
        
        # Top expertise areas
        top_expertise = sorted(self.topic_expertise.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Recent learning activity
        recent_learning = len([h for h in self.learning_history if time.time() - h['timestamp'] < 3600])
        
        return {
            "total_insights": len(self.knowledge_items),
            "expertise_areas": [area for area, level in top_expertise if level > 0.5],
            "learning_activity": "active" if recent_learning > 2 else "moderate" if recent_learning > 0 else "dormant",
            "problem_solving_capable": len(top_expertise) > 0 and top_expertise[0][1] > 1.0
        }

# Integration functions
def create_data_processor():
    """Create the data processing system"""
    return OrganismDataProcessor()

def process_organism_food_consumption(organism, food_morsel, data_processor):
    """Process real data when organism consumes food"""
    
    # Create knowledge base if organism doesn't have one
    if not hasattr(organism, 'knowledge_base'):
        organism.knowledge_base = OrganismKnowledgeBase()
    
    # Extract real knowledge from the data
    knowledge_extracted = data_processor.process_real_data(food_morsel, organism.capabilities)
    
    if knowledge_extracted:
        # Add knowledge to organism
        organism.knowledge_base.add_knowledge(knowledge_extracted, organism.id)
        
        # Organisms get smarter as they learn
        if hasattr(organism.traits, 'learning_rate'):
            organism.traits.learning_rate *= (1.0 + len(knowledge_extracted) * 0.01)
        
        # Generate insights occasionally  
        if len(knowledge_extracted) > 1:
            insight = organism.knowledge_base.generate_insight()
            if insight:
                print(f"💡 Organism {organism.id} insight: {insight}")
        
        return True
    
    return False

# Example usage
if __name__ == "__main__":
    print("🧠 Testing Real Data Processing...")
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Create processor
    processor = create_data_processor()
    
    # Simulate RSS data
    from data_sources.harvesters import DataMorsel, DataType
    
    rss_morsel = DataMorsel(
        data_type=DataType.XML_DATA,
        content="Title: New AI breakthrough in machine learning efficiency\nSummary: Researchers develop revolutionary algorithm for faster neural network training",
        size=100,
        source="RSS:Tech News",
        timestamp=time.time(),
        energy_value=15
    )
    
    # Simulate organism capabilities
    from genesis.evolution import Capability
    capabilities = {Capability.PATTERN_MATCH, Capability.ABSTRACT}
    
    # Process the data
    knowledge = processor.process_real_data(rss_morsel, capabilities)
    
    print(f"Extracted {len(knowledge)} knowledge items:")
    for k in knowledge:
        print(f"  - {k.insight_type.value}: {k.content}")
        print(f"    Keywords: {k.keywords}")
        print(f"    Usefulness: {k.usefulness}")
    
    print("✅ Data processing test complete!")