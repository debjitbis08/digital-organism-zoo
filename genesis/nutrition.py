# Advanced Nutrition System for Digital Organisms
# Sophisticated energy metabolism and scarcity mechanics

import random
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

# Import from data sources
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_sources.harvesters import DataType, DataMorsel

class NutritionalCategory(Enum):
    """Categories of nutritional value"""
    SIMPLE_CARBS = "simple_carbs"      # Quick energy, fast decay
    COMPLEX_CARBS = "complex_carbs"    # Sustained energy
    PROTEIN = "protein"                # Growth and capability development
    MINERALS = "minerals"              # Resilience and stability
    VITAMINS = "vitamins"              # Cognitive enhancement
    FIBER = "fiber"                    # Memory and storage efficiency

@dataclass
class NutritionalProfile:
    """Detailed nutritional breakdown of data"""
    base_energy: int
    category: NutritionalCategory
    processing_difficulty: int        # 1-5 scale
    required_capabilities: List[str]  # Capability names needed
    
    # Nutritional components (0.0-1.0)
    carbs: float = 0.0
    protein: float = 0.0
    minerals: float = 0.0
    vitamins: float = 0.0
    fiber: float = 0.0
    
    # Metabolic effects
    energy_decay_rate: float = 0.1    # How fast energy decays
    learning_boost: float = 0.0       # Temporary learning rate increase
    curiosity_boost: float = 0.0     # Temporary curiosity increase
    creativity_boost: float = 0.0    # Temporary creativity increase
    
    # Special properties
    is_addictive: bool = False        # Organism craves this type
    spoilage_rate: float = 0.1       # How fast food spoils
    toxicity: float = 0.0            # Can harm organism if too much

class NutritionDatabase:
    """Database of nutritional profiles for different data types"""
    
    def __init__(self):
        self.profiles = self._create_nutrition_profiles()
        self.metabolic_history = {}  # Track what organisms have eaten
    
    def _create_nutrition_profiles(self) -> Dict[DataType, NutritionalProfile]:
        """Create detailed nutritional profiles for each data type"""
        return {
            DataType.SIMPLE_TEXT: NutritionalProfile(
                base_energy=5,
                category=NutritionalCategory.SIMPLE_CARBS,
                processing_difficulty=1,
                required_capabilities=["EAT_TEXT"],
                carbs=0.8, protein=0.1, fiber=0.1,
                energy_decay_rate=0.2,  # Burns fast
                learning_boost=0.0,
                spoilage_rate=0.3
            ),
            
            DataType.STRUCTURED_JSON: NutritionalProfile(
                base_energy=12,
                category=NutritionalCategory.COMPLEX_CARBS,
                processing_difficulty=2,
                required_capabilities=["PATTERN_MATCH"],
                carbs=0.6, protein=0.2, vitamins=0.2,
                energy_decay_rate=0.1,
                learning_boost=0.1,  # Structured data helps learning
                spoilage_rate=0.2
            ),
            
            DataType.XML_DATA: NutritionalProfile(
                base_energy=10,
                category=NutritionalCategory.COMPLEX_CARBS,
                processing_difficulty=2,
                required_capabilities=["PATTERN_MATCH"],
                carbs=0.5, protein=0.2, minerals=0.2, fiber=0.1,
                energy_decay_rate=0.15,
                learning_boost=0.05,
                spoilage_rate=0.25
            ),
            
            DataType.CODE: NutritionalProfile(
                base_energy=25,
                category=NutritionalCategory.PROTEIN,
                processing_difficulty=4,
                required_capabilities=["ABSTRACT"],
                protein=0.7, vitamins=0.2, minerals=0.1,
                energy_decay_rate=0.05,  # Very efficient
                learning_boost=0.3,
                curiosity_boost=0.2,
                creativity_boost=0.4,  # Code inspires creativity
                spoilage_rate=0.1,  # Code doesn't spoil easily
                is_addictive=True   # Organisms crave code
            ),
            
            DataType.REAL_TIME_STREAM: NutritionalProfile(
                base_energy=15,
                category=NutritionalCategory.VITAMINS,
                processing_difficulty=3,
                required_capabilities=["RECEIVE", "PATTERN_MATCH"],
                vitamins=0.6, carbs=0.3, fiber=0.1,
                energy_decay_rate=0.05,  # Continuous feeding
                learning_boost=0.2,
                curiosity_boost=0.4,
                spoilage_rate=0.05,  # Always fresh
                toxicity=0.1  # Can overwhelm if too much
            ),
            
            DataType.BINARY: NutritionalProfile(
                base_energy=30,
                category=NutritionalCategory.MINERALS,
                processing_difficulty=5,
                required_capabilities=["READ_SELF", "ABSTRACT"],
                minerals=0.8, protein=0.2,
                energy_decay_rate=0.02,  # Very stable energy
                learning_boost=0.1,
                creativity_boost=0.3,
                spoilage_rate=0.0,  # Never spoils
                toxicity=0.2  # Hard to digest
            )
        }
    
    def get_nutritional_profile(self, data_type: DataType) -> NutritionalProfile:
        """Get nutritional profile for a data type"""
        return self.profiles.get(data_type, self.profiles[DataType.SIMPLE_TEXT])
    
    def calculate_effective_energy(self, morsel: DataMorsel, organism_state: Dict) -> Tuple[int, Dict]:
        """Calculate actual energy gained considering organism state"""
        profile = self.get_nutritional_profile(morsel.data_type)
        
        # Base energy calculation
        base_energy = profile.base_energy
        
        # Size multiplier (larger data = more energy, but diminishing returns)
        size_multiplier = 1.0 + math.log(max(1, morsel.size / 100)) * 0.1
        
        # Freshness impact
        freshness_multiplier = morsel.freshness
        
        # Organism state impacts
        state_multipliers = self._calculate_state_multipliers(profile, organism_state)
        
        # Calculate final energy
        effective_energy = int(
            base_energy * 
            size_multiplier * 
            freshness_multiplier * 
            state_multipliers['energy']
        )
        
        # Calculate metabolic effects
        effects = {
            'energy_gained': effective_energy,
            'learning_boost': profile.learning_boost * state_multipliers['learning'],
            'curiosity_boost': profile.curiosity_boost * state_multipliers['curiosity'],
            'creativity_boost': profile.creativity_boost * state_multipliers['creativity'],
            'toxicity_damage': profile.toxicity * state_multipliers['toxicity']
        }
        
        return effective_energy, effects
    
    def _calculate_state_multipliers(self, profile: NutritionalProfile, organism_state: Dict) -> Dict[str, float]:
        """Calculate how organism state affects nutrition absorption"""
        multipliers = {
            'energy': 1.0,
            'learning': 1.0,
            'curiosity': 1.0,
            'creativity': 1.0,
            'toxicity': 1.0
        }
        
        # Energy level affects efficiency
        energy_level = organism_state.get('energy', 100)
        if energy_level < 20:
            # Starving organisms absorb more energy but process poorly
            multipliers['energy'] = 1.5
            multipliers['learning'] = 0.5
        elif energy_level > 150:
            # Well-fed organisms are more efficient at complex processing
            multipliers['learning'] = 1.3
            multipliers['creativity'] = 1.2
        
        # Age affects metabolism
        age = organism_state.get('age', 0)
        if age < 50:
            # Young organisms learn faster
            multipliers['learning'] = multipliers['learning'] * 1.2
        elif age > 500:
            # Old organisms are more efficient but less adaptable
            multipliers['energy'] = multipliers['energy'] * 1.1
            multipliers['curiosity'] = multipliers['curiosity'] * 0.8
        
        # Frustration affects processing
        frustration = organism_state.get('frustration', 0.0)
        if frustration > 0.5:
            # Frustrated organisms process food poorly
            multipliers['energy'] = multipliers['energy'] * (1.0 - frustration * 0.3)
            multipliers['toxicity'] = multipliers['toxicity'] * (1.0 + frustration)
        
        # Intelligence affects complex food processing
        intelligence = organism_state.get('intelligence', 0.1)
        if profile.processing_difficulty > 2:
            multipliers['energy'] = multipliers['energy'] * (0.5 + intelligence)
            multipliers['learning'] = multipliers['learning'] * (0.8 + intelligence * 0.4)
        
        return multipliers

class ScarcityManager:
    """Manages advanced scarcity mechanics and resource competition"""
    
    def __init__(self):
        self.global_scarcity = 1.0  # 1.0 = abundant, 0.0 = famine
        self.type_scarcity = {}     # Per-data-type scarcity
        self.seasonal_modifiers = {}
        self.competition_pressure = 0.0
        self.last_update = time.time()
        
        # Historical tracking
        self.consumption_history = []
        self.population_pressure = 0.0
    
    def update_scarcity(self, ecosystem_stats: Dict, population_size: int):
        """Update scarcity based on ecosystem state and population"""
        current_time = time.time()
        time_delta = current_time - self.last_update
        
        # Calculate global scarcity
        total_food = ecosystem_stats.get('total_food_available', 0)
        total_consumption = ecosystem_stats.get('total_food_consumed', 0)
        
        # Population pressure - more organisms = more scarcity
        self.population_pressure = min(2.0, population_size / 5.0)  # Baseline: 5 organisms
        
        # Base scarcity from food availability
        if total_food > 0:
            base_scarcity = min(1.0, total_food / (population_size * 10))  # 10 food per organism = abundant
        else:
            base_scarcity = 0.0
        
        # Apply population pressure
        self.global_scarcity = base_scarcity / self.population_pressure
        
        # Calculate per-type scarcity
        food_by_type = ecosystem_stats.get('food_by_type', {})
        for data_type_str, count in food_by_type.items():
            type_scarcity = min(1.0, count / (population_size * 2))  # 2 per organism per type
            self.type_scarcity[data_type_str] = type_scarcity
        
        # Seasonal variations (simulate daily/weekly cycles)
        season_modifier = 0.8 + 0.4 * math.sin(current_time / 3600)  # Hourly cycle for demo
        self.global_scarcity *= season_modifier
        
        # Competition pressure increases with scarcity
        self.competition_pressure = 1.0 - self.global_scarcity
        
        self.last_update = current_time
    
    def should_find_food(self, organism_capabilities: set, preferred_type: Optional[DataType] = None) -> float:
        """Calculate probability that organism finds food based on scarcity"""
        
        # Base probability from global scarcity
        base_prob = self.global_scarcity
        
        # Type-specific scarcity
        if preferred_type:
            type_scarcity = self.type_scarcity.get(preferred_type.value, 0.5)
            base_prob *= type_scarcity
        
        # Competition - more capable organisms have advantage in scarcity
        capability_advantage = len(organism_capabilities) / 26.0  # 26 total capabilities
        competition_modifier = 1.0 - (self.competition_pressure * (1.0 - capability_advantage))
        
        final_probability = base_prob * competition_modifier
        
        return max(0.0, min(1.0, final_probability))
    
    def apply_scarcity_effects(self, morsel: DataMorsel) -> DataMorsel:
        """Modify food morsel based on scarcity conditions"""
        
        # Scarcity makes food less nutritious (desperation eating)
        scarcity_factor = max(0.3, self.global_scarcity)
        morsel.energy_value = int(morsel.energy_value * scarcity_factor)
        
        # Competition makes food decay faster
        competition_decay = 1.0 + self.competition_pressure
        morsel.decay_freshness(competition_decay)
        
        # High competition might make food "contaminated" (lower quality)
        if self.competition_pressure > 0.7 and random.random() < 0.3:
            morsel.energy_value = int(morsel.energy_value * 0.7)
        
        return morsel
    
    def get_scarcity_report(self) -> Dict:
        """Get detailed scarcity report"""
        return {
            'global_scarcity': self.global_scarcity,
            'population_pressure': self.population_pressure,
            'competition_pressure': self.competition_pressure,
            'type_scarcity': self.type_scarcity.copy(),
            'scarcity_level': self._get_scarcity_level_description()
        }
    
    def _get_scarcity_level_description(self) -> str:
        """Get human-readable scarcity level"""
        if self.global_scarcity > 0.8:
            return "abundant"
        elif self.global_scarcity > 0.6:
            return "plentiful"
        elif self.global_scarcity > 0.4:
            return "moderate"
        elif self.global_scarcity > 0.2:
            return "scarce"
        else:
            return "famine"

class MetabolicTracker:
    """Tracks organism metabolism and dietary effects over time"""
    
    def __init__(self):
        self.metabolic_profiles = {}  # organism_id -> metabolic state
        self.dietary_history = {}     # organism_id -> list of consumed food
        
    def track_consumption(self, organism_id: str, morsel: DataMorsel, effects: Dict):
        """Track what organism ate and its effects"""
        
        if organism_id not in self.dietary_history:
            self.dietary_history[organism_id] = []
            self.metabolic_profiles[organism_id] = {
                'total_energy_consumed': 0,
                'preferred_foods': {},
                'dietary_balance': {
                    'carbs': 0.0,
                    'protein': 0.0,
                    'vitamins': 0.0,
                    'minerals': 0.0,
                    'fiber': 0.0
                },
                'addiction_levels': {},
                'toxin_buildup': 0.0,
                'metabolic_efficiency': 1.0
            }
        
        # Record consumption
        consumption_record = {
            'timestamp': time.time(),
            'data_type': morsel.data_type.value,
            'energy_gained': effects['energy_gained'],
            'source': morsel.source,
            'effects': effects.copy()
        }
        
        self.dietary_history[organism_id].append(consumption_record)
        
        # Update metabolic profile
        profile = self.metabolic_profiles[organism_id]
        profile['total_energy_consumed'] += effects['energy_gained']
        
        # Track food preferences
        food_type = morsel.data_type.value
        if food_type not in profile['preferred_foods']:
            profile['preferred_foods'][food_type] = 0
        profile['preferred_foods'][food_type] += 1
        
        # Track toxin buildup
        profile['toxin_buildup'] += effects.get('toxicity_damage', 0)
        profile['toxin_buildup'] = max(0, profile['toxin_buildup'] - 0.01)  # Natural detox
        
        # Calculate metabolic efficiency based on dietary balance
        self._update_metabolic_efficiency(organism_id)
        
        # Trim old history (keep last 100 meals)
        if len(self.dietary_history[organism_id]) > 100:
            self.dietary_history[organism_id] = self.dietary_history[organism_id][-100:]
    
    def _update_metabolic_efficiency(self, organism_id: str):
        """Update organism's metabolic efficiency based on diet balance"""
        profile = self.metabolic_profiles[organism_id]
        recent_meals = self.dietary_history[organism_id][-20:]  # Last 20 meals
        
        if not recent_meals:
            return
        
        # Calculate dietary diversity
        food_types = set(meal['data_type'] for meal in recent_meals)
        diversity_bonus = len(food_types) / 6.0  # 6 possible data types
        
        # Calculate nutritional balance (simplified)
        avg_energy = sum(meal['energy_gained'] for meal in recent_meals) / len(recent_meals)
        
        # Base efficiency from diversity and balance
        base_efficiency = 0.7 + (diversity_bonus * 0.3)
        
        # Penalties
        toxin_penalty = min(0.3, profile['toxin_buildup'] * 0.1)
        
        profile['metabolic_efficiency'] = max(0.3, base_efficiency - toxin_penalty)
    
    def get_dietary_recommendations(self, organism_id: str) -> List[str]:
        """Get recommendations for organism's diet"""
        if organism_id not in self.metabolic_profiles:
            return ["Try eating a variety of data types for balanced nutrition"]
        
        profile = self.metabolic_profiles[organism_id]
        recommendations = []
        
        # Check dietary diversity
        food_types = len(profile['preferred_foods'])
        if food_types < 3:
            recommendations.append("Eat more diverse data types for better metabolic efficiency")
        
        # Check toxin levels
        if profile['toxin_buildup'] > 0.5:
            recommendations.append("Avoid complex data temporarily to reduce toxin buildup")
        
        # Check for addictions
        if profile['preferred_foods']:
            max_food = max(profile['preferred_foods'], key=profile['preferred_foods'].get)
            max_count = profile['preferred_foods'][max_food]
            total_meals = sum(profile['preferred_foods'].values())
            
            if max_count / total_meals > 0.7:
                recommendations.append(f"Reduce dependence on {max_food} - try other food types")
        
        if not recommendations:
            recommendations.append("Dietary balance is good - keep exploring new data types!")
        
        return recommendations

# Integration functions for easy use with existing organism system

def create_enhanced_nutrition_system():
    """Create the complete enhanced nutrition system"""
    return {
        'nutrition_db': NutritionDatabase(),
        'scarcity_manager': ScarcityManager(),
        'metabolic_tracker': MetabolicTracker()
    }

def process_organism_feeding(organism, morsel: DataMorsel, nutrition_system: Dict) -> Dict:
    """Process organism feeding with enhanced nutrition"""
    
    # Get organism state
    organism_state = {
        'energy': organism.energy,
        'age': organism.age,
        'frustration': organism.frustration,
        'intelligence': organism.intelligence,
        'capabilities': organism.capabilities
    }
    
    # Calculate nutritional effects
    nutrition_db = nutrition_system['nutrition_db']
    energy_gained, effects = nutrition_db.calculate_effective_energy(morsel, organism_state)
    
    # Apply scarcity effects
    scarcity_manager = nutrition_system['scarcity_manager']
    modified_morsel = scarcity_manager.apply_scarcity_effects(morsel)
    
    # Track consumption
    metabolic_tracker = nutrition_system['metabolic_tracker']
    metabolic_tracker.track_consumption(organism.id, modified_morsel, effects)
    
    # Apply effects to organism
    organism.energy += effects['energy_gained']
    
    # Temporary boosts
    if effects['learning_boost'] > 0:
        organism.traits.learning_rate *= (1.0 + effects['learning_boost'])
    if effects['curiosity_boost'] > 0:
        organism.traits.curiosity *= (1.0 + effects['curiosity_boost'])
    if effects['creativity_boost'] > 0:
        organism.traits.creativity *= (1.0 + effects['creativity_boost'])
    
    # Toxicity damage
    if effects['toxicity_damage'] > 0:
        organism.energy -= int(effects['toxicity_damage'] * 10)
        organism.frustration += effects['toxicity_damage'] * 0.1
    
    return {
        'effects': effects,
        'recommendations': metabolic_tracker.get_dietary_recommendations(organism.id)
    }

# Example usage and testing
if __name__ == "__main__":
    print("🧬 Testing Enhanced Nutrition System...")
    
    # Create nutrition system
    nutrition_system = create_enhanced_nutrition_system()
    
    # Test nutritional profiles
    nutrition_db = nutrition_system['nutrition_db']
    
    for data_type in DataType:
        profile = nutrition_db.get_nutritional_profile(data_type)
        print(f"{data_type.value}: {profile.base_energy} energy, "
              f"{profile.category.value}, difficulty {profile.processing_difficulty}")
    
    print("\n✅ Enhanced nutrition system ready!")