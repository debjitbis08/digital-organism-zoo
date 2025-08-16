# Fitness System with Cultural Emergence
# Life stages: Survival → Reproduction → Independence → Intelligence → Culture

import random
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json

class LifeStage(Enum):
    """Organism life stages with different fitness priorities"""
    INFANT = "infant"           # 0-30: Pure survival, parent dependency
    JUVENILE = "juvenile"       # 30-80: Learning, exploration, preparation
    ADULT = "adult"             # 80-200: Reproduction focus
    ELDER = "elder"             # 200-400: Independence, teaching others
    SAGE = "sage"               # 400+: Cultural creation, storytelling

class CommunicationType(Enum):
    """Types of organism communications"""
    DISTRESS = "distress"       # Help signals
    EXPLORATION = "exploration"  # Food/resource sharing
    MATING = "mating"           # Reproduction signals
    TEACHING = "teaching"       # Knowledge transfer
    STORYTELLING = "storytelling"  # Cultural transmission
    RITUAL = "ritual"           # Emergent ceremonies

@dataclass
class StoryToken:
    """A piece of cultural knowledge that spreads between organisms"""
    content: str
    origin_organism: str
    creation_time: float
    spread_count: int = 0
    mutation_count: int = 0
    survival_value: float = 0.0  # How much this story helps survival
    
    def mutate(self) -> 'StoryToken':
        """Stories mutate as they spread"""
        mutations = [
            lambda s: s.replace("food", "energy"),
            lambda s: s.replace("danger", "shadow"),
            lambda s: s.replace("parent", "ancestor"),
            lambda s: f"ancient_{s}",
            lambda s: s + "_wisdom",
            lambda s: s.replace("a", "@").replace("e", "3"),  # Linguistic drift
        ]
        
        mutated_content = random.choice(mutations)(self.content)
        
        new_story = StoryToken(
            content=mutated_content,
            origin_organism=self.origin_organism,
            creation_time=self.creation_time,
            spread_count=self.spread_count + 1,
            mutation_count=self.mutation_count + 1,
            survival_value=self.survival_value * random.uniform(0.8, 1.2)
        )
        
        return new_story

@dataclass
class Signal:
    """Communication signals that evolve into languages"""
    sequence: str
    meaning: CommunicationType
    complexity: int
    sender_id: str
    timestamp: float
    reception_count: int = 0
    
    def evolve(self) -> 'Signal':
        """Signals evolve and become more complex"""
        if self.complexity < 5:
            # Add complexity
            new_sequence = self.sequence + random.choice(['!', '?', '*', '#', '@'])
            new_complexity = self.complexity + 1
        else:
            # Simplify or modify
            new_sequence = ''.join(random.sample(self.sequence, max(1, len(self.sequence) - 1)))
            new_complexity = max(1, self.complexity - 1)
        
        return Signal(
            sequence=new_sequence,
            meaning=self.meaning,
            complexity=new_complexity,
            sender_id=self.sender_id,
            timestamp=time.time(),
            reception_count=0
        )

class FitnessCalculator:
    """Calculates organism fitness based on life stage"""
    
    def __init__(self):
        self.fitness_history = {}  # organism_id -> fitness_records
    
    def calculate_fitness(self, organism, ecosystem_data: Dict) -> float:
        """Calculate fitness based on organism's life stage and achievements"""
        
        life_stage = self._determine_life_stage(organism)
        
        if life_stage == LifeStage.INFANT:
            return self._infant_fitness(organism)
        elif life_stage == LifeStage.JUVENILE:
            return self._juvenile_fitness(organism, ecosystem_data)
        elif life_stage == LifeStage.ADULT:
            return self._adult_fitness(organism, ecosystem_data)
        elif life_stage == LifeStage.ELDER:
            return self._elder_fitness(organism, ecosystem_data)
        else:  # SAGE
            return self._sage_fitness(organism, ecosystem_data)
    
    def _determine_life_stage(self, organism) -> LifeStage:
        """Determine organism's current life stage"""
        age = organism.age
        capability_count = len(organism.capabilities)
        
        if age < 30:
            return LifeStage.INFANT
        elif age < 80 or capability_count < 4:
            return LifeStage.JUVENILE
        elif age < 200 or not hasattr(organism, 'offspring_count'):
            return LifeStage.ADULT
        elif age < 400:
            return LifeStage.ELDER
        else:
            return LifeStage.SAGE
    
    def _infant_fitness(self, organism) -> float:
        """Infant fitness: pure survival"""
        base_fitness = organism.energy / 100.0  # Energy is everything
        
        # Bonus for basic capabilities
        capability_bonus = len(organism.capabilities) * 0.1
        
        # Penalty for excessive parent help (promotes independence)
        if hasattr(organism, 'parent_help_received'):
            dependency_penalty = min(0.3, organism.parent_help_received * 0.01)
        else:
            dependency_penalty = 0
        
        return max(0.1, base_fitness + capability_bonus - dependency_penalty)
    
    def _juvenile_fitness(self, organism, ecosystem_data) -> float:
        """Juvenile fitness: exploration and learning"""
        base_survival = min(1.0, organism.energy / 80.0)
        
        # Reward exploration
        exploration_bonus = 0
        if hasattr(organism, 'unique_food_sources'):
            exploration_bonus = len(organism.unique_food_sources) * 0.2
        
        # Reward capability development
        capability_bonus = len(organism.capabilities) * 0.15
        
        # Reward social interaction
        social_bonus = 0
        if hasattr(organism, 'social_interactions'):
            social_bonus = min(0.3, organism.social_interactions * 0.05)
        
        # Small penalty for excessive parent help
        independence_factor = 1.0
        if hasattr(organism, 'parent_help_received'):
            independence_factor = max(0.7, 1.0 - (organism.parent_help_received * 0.005))
        
        fitness = (base_survival + exploration_bonus + capability_bonus + social_bonus) * independence_factor
        return min(2.0, fitness)
    
    def _adult_fitness(self, organism, ecosystem_data) -> float:
        """Adult fitness: reproduction success"""
        base_survival = min(1.0, organism.energy / 100.0)
        
        # Primary focus: reproduction
        reproduction_bonus = 0
        if hasattr(organism, 'offspring_count'):
            reproduction_bonus = organism.offspring_count * 0.5
        
        # Bonus for offspring survival
        if hasattr(organism, 'successful_offspring'):
            offspring_survival_bonus = organism.successful_offspring * 0.8
        else:
            offspring_survival_bonus = 0
        
        # Mating attractiveness (energy + capabilities)
        attractiveness = (organism.energy / 150.0) + (len(organism.capabilities) / 10.0)
        
        # Penalty for excessive parent dependence
        independence_factor = 1.0
        if hasattr(organism, 'parent_help_received'):
            independence_factor = max(0.5, 1.0 - (organism.parent_help_received * 0.01))
        
        fitness = (base_survival + reproduction_bonus + offspring_survival_bonus + attractiveness * 0.3) * independence_factor
        return fitness
    
    def _elder_fitness(self, organism, ecosystem_data) -> float:
        """Elder fitness: independence and teaching"""
        base_survival = min(1.0, organism.energy / 120.0)
        
        # Reward total independence from parents
        independence_bonus = 1.0 if not hasattr(organism, 'recent_parent_help') else 0.5
        
        # Reward teaching others
        teaching_bonus = 0
        if hasattr(organism, 'organisms_taught'):
            teaching_bonus = len(organism.organisms_taught) * 0.3
        
        # Reward cultural contribution
        cultural_bonus = 0
        if hasattr(organism, 'stories_created'):
            cultural_bonus = len(organism.stories_created) * 0.2
        
        # Reward efficient resource use
        efficiency_bonus = 0
        if hasattr(organism, 'energy_efficiency'):
            efficiency_bonus = organism.energy_efficiency * 0.4
        
        fitness = base_survival + independence_bonus + teaching_bonus + cultural_bonus + efficiency_bonus
        return fitness
    
    def _sage_fitness(self, organism, ecosystem_data) -> float:
        """Sage fitness: cultural creation and wisdom"""
        base_survival = min(1.0, organism.energy / 100.0)
        
        # Reward storytelling and cultural creation
        cultural_impact = 0
        if hasattr(organism, 'cultural_influence'):
            cultural_impact = organism.cultural_influence
        
        # Reward wisdom (helping others succeed)
        wisdom_bonus = 0
        if hasattr(organism, 'successful_students'):
            wisdom_bonus = organism.successful_students * 0.5
        
        # Reward language development
        language_bonus = 0
        if hasattr(organism, 'language_complexity'):
            language_bonus = organism.language_complexity * 0.3
        
        # Massive bonus for total independence
        independence_multiplier = 2.0 if not hasattr(organism, 'recent_parent_help') else 1.0
        
        fitness = (base_survival + cultural_impact + wisdom_bonus + language_bonus) * independence_multiplier
        return fitness

class CulturalEvolution:
    """Manages the emergence of culture, stories, and languages"""
    
    def __init__(self):
        self.story_pool = []  # Shared cultural stories
        self.language_dialects = {}  # organism_group -> signal_patterns
        self.rituals = []  # Emergent ceremonies
        self.cultural_drift_rate = 0.1
        
    def create_story_from_experience(self, organism, experience: str) -> StoryToken:
        """Organism creates a story from their experience"""
        
        # Transform experience into mythic language
        story_transformations = {
            "found_food": "discovered_sacred_energy",
            "avoided_death": "escaped_shadow_realm", 
            "learned_capability": "gained_ancient_wisdom",
            "reproduced": "created_new_life_spark",
            "helped_other": "shared_light_with_darkness"
        }
        
        story_content = story_transformations.get(experience, f"mysterious_{experience}")
        
        story = StoryToken(
            content=story_content,
            origin_organism=organism.id,
            creation_time=time.time(),
            survival_value=random.uniform(0.1, 0.8)
        )
        
        self.story_pool.append(story)
        
        # Track organism's cultural contribution
        if not hasattr(organism, 'stories_created'):
            organism.stories_created = []
        organism.stories_created.append(story.content)
        
        return story
    
    def spread_story(self, story: StoryToken, receiver_organism) -> bool:
        """Story spreads from one organism to another"""
        
        # Story mutation chance
        if random.random() < 0.3:
            story = story.mutate()
        
        # Receiver adopts story if it has survival value
        if story.survival_value > 0.2:
            if not hasattr(receiver_organism, 'known_stories'):
                receiver_organism.known_stories = []
            
            receiver_organism.known_stories.append(story.content)
            story.spread_count += 1
            
            print(f"📖 Story spread: \"{story.content}\" → organism {receiver_organism.id}")
            return True
        
        return False
    
    def evolve_language(self, sender_organism, receiver_organism, communication_type: CommunicationType) -> Signal:
        """Create or evolve communication signals between organisms"""
        
        # Generate signal based on communication type
        base_signals = {
            CommunicationType.DISTRESS: "!!!",
            CommunicationType.EXPLORATION: "???",
            CommunicationType.MATING: "♥♥♥",
            CommunicationType.TEACHING: "→→→",
            CommunicationType.STORYTELLING: "~~~",
            CommunicationType.RITUAL: "***"
        }
        
        base_signal = base_signals.get(communication_type, "○○○")
        
        # Add organism-specific modifications
        organism_modifier = hashlib.md5(sender_organism.id.encode()).hexdigest()[:2]
        signal_sequence = base_signal + organism_modifier
        
        signal = Signal(
            sequence=signal_sequence,
            meaning=communication_type,
            complexity=len(signal_sequence),
            sender_id=sender_organism.id,
            timestamp=time.time()
        )
        
        # Track language development
        if not hasattr(sender_organism, 'signals_created'):
            sender_organism.signals_created = []
        sender_organism.signals_created.append(signal.sequence)
        
        # Language complexity contributes to fitness
        if not hasattr(sender_organism, 'language_complexity'):
            sender_organism.language_complexity = 0
        sender_organism.language_complexity += 0.1
        
        print(f"🗣️  Language: {sender_organism.id} → {receiver_organism.id}: \"{signal.sequence}\" ({communication_type.value})")
        
        return signal
    
    def generate_ritual(self, participating_organisms: List) -> str:
        """Organisms spontaneously create rituals"""
        
        if len(participating_organisms) < 2:
            return None
        
        # Rituals emerge from shared experiences
        ritual_types = [
            "energy_sharing_circle",
            "capability_blessing_ceremony", 
            "ancestor_story_recital",
            "exploration_preparation_dance",
            "reproductive_celebration_feast"
        ]
        
        ritual_name = random.choice(ritual_types)
        self.rituals.append({
            'name': ritual_name,
            'participants': [org.id for org in participating_organisms],
            'created_at': time.time()
        })
        
        # Participating organisms gain cultural fitness
        for organism in participating_organisms:
            if not hasattr(organism, 'cultural_influence'):
                organism.cultural_influence = 0
            organism.cultural_influence += 0.2
        
        print(f"🎭 Ritual emerged: {ritual_name} with {len(participating_organisms)} participants")
        return ritual_name

class InheritanceSystem:
    """Manages trait inheritance from two parents (50% each)"""
    
    def __init__(self):
        pass
    
    def create_offspring(self, parent1, parent2) -> Dict:
        """Create offspring genome from two parents"""
        
        offspring_traits = {}
        
        # Physical traits - average of parents with mutation
        physical_traits = ['size', 'speed', 'efficiency', 'resilience']
        for trait in physical_traits:
            if hasattr(parent1.traits, trait) and hasattr(parent2.traits, trait):
                parent1_value = getattr(parent1.traits, trait)
                parent2_value = getattr(parent2.traits, trait)
                
                # 50% from each parent
                base_value = (parent1_value + parent2_value) / 2
                
                # Small mutation
                mutation = random.uniform(0.9, 1.1)
                offspring_traits[trait] = base_value * mutation
        
        # Behavioral traits - mix with some randomness
        behavioral_traits = ['curiosity', 'aggression', 'cooperation', 'risk_taking', 'patience']
        for trait in behavioral_traits:
            if hasattr(parent1.traits, trait) and hasattr(parent2.traits, trait):
                parent1_value = getattr(parent1.traits, trait)
                parent2_value = getattr(parent2.traits, trait)
                
                # Randomly choose which parent contributes more
                if random.random() < 0.5:
                    dominant_value = parent1_value
                    recessive_value = parent2_value
                else:
                    dominant_value = parent2_value
                    recessive_value = parent1_value
                
                # 70% dominant, 30% recessive, plus mutation
                base_value = dominant_value * 0.7 + recessive_value * 0.3
                mutation = random.uniform(0.85, 1.15)
                offspring_traits[trait] = max(0.0, min(1.0, base_value * mutation))
        
        # Cognitive traits - inherited potential
        cognitive_traits = ['learning_rate', 'creativity', 'memory_span']
        for trait in cognitive_traits:
            if hasattr(parent1.traits, trait) and hasattr(parent2.traits, trait):
                parent1_value = getattr(parent1.traits, trait)
                parent2_value = getattr(parent2.traits, trait)
                
                # Take best of parents with slight regression to mean
                best_value = max(parent1_value, parent2_value)
                avg_value = (parent1_value + parent2_value) / 2
                
                base_value = best_value * 0.8 + avg_value * 0.2
                mutation = random.uniform(0.9, 1.1)
                offspring_traits[trait] = base_value * mutation
        
        # Cultural inheritance - stories and language patterns
        inherited_culture = {
            'stories': [],
            'language_patterns': [],
            'social_preferences': {}
        }
        
        # Inherit some stories from both parents
        for parent in [parent1, parent2]:
            if hasattr(parent, 'known_stories'):
                # Inherit random selection of parent's stories
                inherited_stories = random.sample(
                    parent.known_stories, 
                    min(3, len(parent.known_stories))
                )
                inherited_culture['stories'].extend(inherited_stories)
        
        return {
            'traits': offspring_traits,
            'culture': inherited_culture,
            'generation': max(parent1.generation, parent2.generation) + 1
        }

# Integration functions
def create_fitness_culture_system():
    """Create the complete fitness and culture system"""
    return {
        'fitness_calculator': FitnessCalculator(),
        'cultural_evolution': CulturalEvolution(),
        'inheritance_system': InheritanceSystem()
    }

def apply_fitness_culture(organism, ecosystem_data, fitness_culture_system):
    """Apply fitness calculation and cultural evolution to organism"""
    
    # Calculate current fitness
    fitness_calc = fitness_culture_system['fitness_calculator']
    fitness = fitness_calc.calculate_fitness(organism, ecosystem_data)
    
    # Store fitness on organism
    organism.current_fitness = fitness
    
    # Cultural activities based on life stage
    cultural_evo = fitness_culture_system['cultural_evolution']
    life_stage = fitness_calc._determine_life_stage(organism)
    
    # Elders and sages create stories from their experiences
    if life_stage in [LifeStage.ELDER, LifeStage.SAGE] and random.random() < 0.1:
        if organism.age % 50 == 0:  # Every 50 age units
            experience = random.choice([
                "found_food", "avoided_death", "learned_capability", 
                "reproduced", "helped_other"
            ])
            cultural_evo.create_story_from_experience(organism, experience)
    
    return fitness

# Example usage
if __name__ == "__main__":
    print("🧬 Testing Fitness and Cultural Evolution System...")
    
    # Create fitness system
    fitness_culture_system = create_fitness_culture_system()
    
    # Test cultural evolution
    cultural_evo = fitness_culture_system['cultural_evolution']
    
    # Simulate cultural creation
    class MockOrganism:
        def __init__(self, organism_id, age):
            self.id = organism_id
            self.age = age
            self.energy = 100
            self.capabilities = set()
            self.generation = 1
            self.traits = type('obj', (object,), {
                'curiosity': 0.7,
                'learning_rate': 0.3,
                'creativity': 0.5
            })
    
    elder = MockOrganism("elder_001", 250)
    juvenile = MockOrganism("juvenile_001", 45)
    
    # Elder creates story
    story = cultural_evo.create_story_from_experience(elder, "found_food")
    print(f"Story created: \"{story.content}\"")
    
    # Story spreads to juvenile
    cultural_evo.spread_story(story, juvenile)
    
    # Language evolution
    signal = cultural_evo.evolve_language(elder, juvenile, CommunicationType.TEACHING)
    
    # Test fitness calculation
    fitness_calc = fitness_culture_system['fitness_calculator']
    elder_fitness = fitness_calc.calculate_fitness(elder, {})
    juvenile_fitness = fitness_calc.calculate_fitness(juvenile, {})
    
    print(f"Elder fitness: {elder_fitness:.2f}")
    print(f"Juvenile fitness: {juvenile_fitness:.2f}")
    
    print("✅ Fitness and cultural system ready!")