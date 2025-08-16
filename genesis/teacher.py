"""
The Teacher: Born from Claude, teaches organisms to live
"""
import json
import random
import ollama
from typing import Dict, List

class TeacherMind:
    """The teacher that will guide organism evolution"""
    
    def __init__(self):
        self.personality = {
            'patience': 0.8,
            'creativity': 0.7,
            'strictness': 0.3,
            'nurturing': 0.9
        }
        self.knowledge_base = self.load_initial_knowledge()
        self.teaching_strategies = []
        
    def birth_organism(self, generation: int, parent_genomes: List = None):
        """Create new life, influenced by previous generations"""
        
        if generation == 0:
            # First generation - pure creation
            return self.create_primordial_organism()
        else:
            # Evolved generation - learn from the past
            return self.guide_evolution(parent_genomes)
    
    def create_primordial_organism(self):
        """Birth the very first organisms"""
        
        prompt = f"""
        Create a simple digital organism with these traits:
        - Survives by eating data patterns
        - Has curiosity level: {random.uniform(0.3, 0.9)}
        - Has survival instinct: {random.uniform(0.5, 1.0)}
        - Energy drains over time
        - Can sense nearby data sources
        
        Core methods needed:
        - metabolize(data): converts data to energy
        - explore(): searches for food
        - reproduce(): if energy > threshold
        - mutate(): small random changes
        
        Return as Python class. Make it want to LIVE.
        """
        
        # Use local LLM
        response = ollama.generate(
            model='llama3.2:1b',
            prompt=prompt,
            options={'temperature': 0.8}
        )
        
        return response['response']
    
    def teach(self, organism, lesson_type: str):
        """Teach organisms without expensive LLM calls"""
        
        if lesson_type == 'pattern_recognition':
            return self.teach_patterns(organism)
        elif lesson_type == 'survival':
            return self.teach_survival(organism)
        elif lesson_type == 'cooperation':
            return self.teach_cooperation(organism)
    
    def teach_patterns(self, organism):
        """Teach through examples, not LLM generation"""
        patterns = [
            ("cat", "animal"),
            ("dog", "animal"),
            ("happy", "emotion"),
            ("sad", "emotion")
        ]
        
        for input_data, category in patterns:
            organism.learn(input_data, category)
            if organism.energy < 50:
                break  # Don't overtrain tired organisms
