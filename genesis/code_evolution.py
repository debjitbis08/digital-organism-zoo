# Code Evolution System: Parent/Teacher can modify organism code permanently
# Enables true digital evolution through code modification

import ast
import inspect
import textwrap
import hashlib
import json
import time
import os
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import importlib.util
import tempfile

class ModificationType(Enum):
    """Types of code modifications"""
    CAPABILITY_ADDITION = "capability_addition"     # Add new capability method
    BEHAVIOR_MODIFICATION = "behavior_modification" # Modify existing behavior
    EFFICIENCY_IMPROVEMENT = "efficiency_improvement" # Optimize existing code
    SAFETY_FIX = "safety_fix"                      # Fix dangerous behaviors
    LEARNING_ENHANCEMENT = "learning_enhancement"   # Improve learning mechanisms
    SURVIVAL_ADAPTATION = "survival_adaptation"    # Adapt to environment changes

@dataclass
class CodeModification:
    """A permanent code modification made to an organism"""
    modification_id: str
    modification_type: ModificationType
    target_method: str
    original_code: str
    modified_code: str
    reason: str
    created_by: str  # "parent", "self", "peer"
    timestamp: float
    success_rate: float = 0.0  # How successful this modification has been
    inheritance_count: int = 0  # How many offspring inherited this
    
    def __post_init__(self):
        if not self.modification_id:
            self.modification_id = hashlib.md5(
                f"{self.target_method}{self.timestamp}".encode()
            ).hexdigest()[:8]

class OrganismCodeTemplate:
    """Template for generating organism code with modifications"""
    
    def __init__(self):
        self.base_template = self._get_base_organism_template()
        self.method_templates = self._get_method_templates()
    
    def _get_base_organism_template(self) -> str:
        """Base organism class template"""
        return '''
class ModifiedOrganism:
    """Dynamically modified organism with evolved code"""
    
    def __init__(self, base_organism):
        # Copy all attributes from base organism
        for attr_name in dir(base_organism):
            if not attr_name.startswith('_'):
                try:
                    setattr(self, attr_name, getattr(base_organism, attr_name))
                except:
                    pass
        
        # Add modification tracking
        self.code_modifications = getattr(base_organism, 'code_modifications', [])
        self.code_version = getattr(base_organism, 'code_version', 1) + 1
        self.last_modified = time.time()
    
    def get_modification_history(self):
        """Get history of all code modifications"""
        return self.code_modifications
    
    def verify_code_integrity(self):
        """Verify that all modifications are still valid"""
        for mod in self.code_modifications:
            if not self._verify_modification(mod):
                return False
        return True
    
    def _verify_modification(self, modification):
        """Verify a single modification is safe and valid"""
        # Basic safety checks
        dangerous_patterns = ['exec', 'eval', '__import__', 'open', 'file']
        for pattern in dangerous_patterns:
            if pattern in modification.modified_code:
                return False
        return True
'''
    
    def _get_method_templates(self) -> Dict[str, str]:
        """Templates for common method modifications"""
        return {
            'enhanced_food_finding': '''
    def enhanced_food_finding(self, data_ecosystem):
        """Enhanced food finding with pattern recognition"""
        # Look for multiple food sources
        potential_foods = []
        for _ in range(3):  # Try 3 times instead of 1
            food = data_ecosystem.find_food_for_organism(self.capabilities)
            if food:
                potential_foods.append(food)
        
        # Choose best food based on energy/freshness ratio
        if potential_foods:
            best_food = max(potential_foods, 
                          key=lambda f: f.energy_value * f.freshness)
            return best_food
        return None
''',
            
            'social_learning': '''
    def learn_from_peer(self, peer_organism):
        """Learn behaviors from other organisms"""
        if hasattr(peer_organism, 'successful_strategies'):
            # Copy successful strategies
            if not hasattr(self, 'learned_strategies'):
                self.learned_strategies = []
            
            for strategy in peer_organism.successful_strategies:
                if strategy not in self.learned_strategies:
                    self.learned_strategies.append(strategy)
                    self.traits.learning_rate *= 1.05  # Slight improvement
        
        # Social interaction bonus
        self.social_interactions += 1
        return True
''',
            
            'adaptive_metabolism': '''
    def adaptive_metabolism(self, food_morsel):
        """Metabolism that adapts to food scarcity"""
        base_energy = food_morsel.energy_value
        
        # If energy is low, extract more from food
        if self.energy < 30:
            efficiency_bonus = 1.5
        elif self.energy < 60:
            efficiency_bonus = 1.2
        else:
            efficiency_bonus = 1.0
        
        # Learn from experience
        if hasattr(self, 'metabolism_history'):
            self.metabolism_history.append(base_energy * efficiency_bonus)
            # Adapt based on recent history
            recent_avg = sum(self.metabolism_history[-10:]) / min(10, len(self.metabolism_history))
            if recent_avg < 8:  # If getting poor nutrition
                efficiency_bonus *= 1.1
        else:
            self.metabolism_history = []
        
        return int(base_energy * efficiency_bonus)
''',
            
            'emergency_survival': '''
    def emergency_survival_mode(self):
        """Activate when near death to maximize survival chances"""
        if self.energy < 15:
            # Reduce all non-essential activities
            self.traits.curiosity *= 0.5  # Less exploration
            self.traits.cooperation *= 0.3  # More selfish
            
            # Boost efficiency
            self.traits.efficiency *= 1.3
            
            # Request emergency help more aggressively
            if hasattr(self, 'emergency_help_requests'):
                self.emergency_help_requests += 1
            else:
                self.emergency_help_requests = 1
            
            return True
        return False
''',
            
            'pattern_memory': '''
    def enhanced_pattern_memory(self, new_pattern):
        """Remember and categorize patterns for better recognition"""
        if not hasattr(self, 'pattern_library'):
            self.pattern_library = {
                'food_patterns': [],
                'danger_patterns': [],
                'social_patterns': [],
                'success_patterns': []
            }
        
        # Categorize the pattern
        if 'food' in str(new_pattern) or 'energy' in str(new_pattern):
            self.pattern_library['food_patterns'].append(new_pattern)
        elif 'help' in str(new_pattern) or 'parent' in str(new_pattern):
            self.pattern_library['social_patterns'].append(new_pattern)
        else:
            self.pattern_library['success_patterns'].append(new_pattern)
        
        # Limit memory size to prevent bloat
        for category in self.pattern_library:
            if len(self.pattern_library[category]) > 20:
                self.pattern_library[category] = self.pattern_library[category][-20:]
        
        return True
'''
        }

class CodeModificationEngine:
    """Engine for safely modifying organism code"""
    
    def __init__(self):
        self.modification_history = []
        self.safe_modifications_cache = {}
        self.template_engine = OrganismCodeTemplate()
        self.temp_code_dir = tempfile.mkdtemp(prefix="organism_code_")
        
    def analyze_organism_for_modifications(self, organism) -> List[str]:
        """Analyze organism to identify potential beneficial modifications"""
        suggestions = []
        
        # Analyze performance issues
        if hasattr(organism, 'energy_efficiency') and organism.energy_efficiency < 0.5:
            suggestions.append("metabolism_optimization")
        
        # Analyze social interactions
        if organism.social_interactions < 2 and organism.age > 100:
            suggestions.append("social_learning_enhancement")
        
        # Analyze survival struggles
        if organism.energy < 30 and organism.age > 50:
            suggestions.append("emergency_survival_protocols")
        
        # Analyze food finding efficiency
        if hasattr(organism, 'failed_attempts') and organism.failed_attempts > 20:
            suggestions.append("enhanced_food_finding")
        
        # Analyze memory usage
        if len(organism.memory) > 50 and not hasattr(organism, 'pattern_library'):
            suggestions.append("pattern_memory_organization")
        
        return suggestions
    
    def create_modification(self, organism, modification_type: str, reason: str) -> Optional[CodeModification]:
        """Create a code modification for an organism"""
        
        if modification_type == "enhanced_food_finding":
            return self._create_food_finding_modification(organism, reason)
        elif modification_type == "social_learning_enhancement":
            return self._create_social_learning_modification(organism, reason)
        elif modification_type == "metabolism_optimization":
            return self._create_metabolism_modification(organism, reason)
        elif modification_type == "emergency_survival_protocols":
            return self._create_survival_modification(organism, reason)
        elif modification_type == "pattern_memory_organization":
            return self._create_memory_modification(organism, reason)
        else:
            return None
    
    def _create_food_finding_modification(self, organism, reason: str) -> CodeModification:
        """Create enhanced food finding capability"""
        
        original_method = "sense_environment"  # Replace basic sensing
        modified_code = self.template_engine.method_templates['enhanced_food_finding']
        
        modification = CodeModification(
            modification_id="",
            modification_type=ModificationType.EFFICIENCY_IMPROVEMENT,
            target_method=original_method,
            original_code="# Basic sensing logic",
            modified_code=modified_code,
            reason=reason,
            created_by="parent",
            timestamp=time.time()
        )
        
        return modification
    
    def _create_social_learning_modification(self, organism, reason: str) -> CodeModification:
        """Create social learning capability"""
        
        modified_code = self.template_engine.method_templates['social_learning']
        
        modification = CodeModification(
            modification_id="",
            modification_type=ModificationType.CAPABILITY_ADDITION,
            target_method="learn_from_peer",
            original_code="# No social learning",
            modified_code=modified_code,
            reason=reason,
            created_by="parent",
            timestamp=time.time()
        )
        
        return modification
    
    def _create_metabolism_modification(self, organism, reason: str) -> CodeModification:
        """Create adaptive metabolism"""
        
        modified_code = self.template_engine.method_templates['adaptive_metabolism']
        
        modification = CodeModification(
            modification_id="",
            modification_type=ModificationType.EFFICIENCY_IMPROVEMENT,
            target_method="process_environment",
            original_code="# Basic metabolism",
            modified_code=modified_code,
            reason=reason,
            created_by="parent",
            timestamp=time.time()
        )
        
        return modification
    
    def _create_survival_modification(self, organism, reason: str) -> CodeModification:
        """Create emergency survival protocols"""
        
        modified_code = self.template_engine.method_templates['emergency_survival']
        
        modification = CodeModification(
            modification_id="",
            modification_type=ModificationType.SURVIVAL_ADAPTATION,
            target_method="live",
            original_code="# Basic life cycle",
            modified_code=modified_code,
            reason=reason,
            created_by="parent",
            timestamp=time.time()
        )
        
        return modification
    
    def _create_memory_modification(self, organism, reason: str) -> CodeModification:
        """Create enhanced pattern memory"""
        
        modified_code = self.template_engine.method_templates['pattern_memory']
        
        modification = CodeModification(
            modification_id="",
            modification_type=ModificationType.LEARNING_ENHANCEMENT,
            target_method="remember_pattern",
            original_code="# Basic memory",
            modified_code=modified_code,
            reason=reason,
            created_by="parent",
            timestamp=time.time()
        )
        
        return modification
    
    def apply_modification_to_organism(self, organism, modification: CodeModification) -> bool:
        """Apply code modification to organism and make it permanent"""
        
        try:
            # Validate modification safety
            if not self._validate_modification_safety(modification):
                print(f"❌ Modification {modification.modification_id} failed safety validation")
                return False
            
            # Generate modified organism class
            modified_class_code = self._generate_modified_organism_code(organism, modification)
            
            # Save to file for persistence
            code_file_path = self._save_organism_code(organism, modified_class_code)
            
            # Apply modification to organism
            self._inject_modification_into_organism(organism, modification)
            
            # Track modification
            if not hasattr(organism, 'code_modifications'):
                organism.code_modifications = []
            organism.code_modifications.append(modification)
            
            # Update organism version
            organism.code_version = getattr(organism, 'code_version', 1) + 1
            organism.last_modified = time.time()
            organism.code_file_path = code_file_path
            
            # Track success
            modification.success_rate = 1.0
            self.modification_history.append(modification)
            
            print(f"🔧 Applied modification {modification.modification_id} to organism {organism.id}")
            print(f"   Type: {modification.modification_type.value}")
            print(f"   Reason: {modification.reason}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply modification {modification.modification_id}: {e}")
            return False
    
    def _validate_modification_safety(self, modification: CodeModification) -> bool:
        """Validate that code modification is safe"""
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'exec', 'eval', '__import__', 'open', 'file', 'input',
            'subprocess', 'os.system', 'os.popen', 'compile'
        ]
        
        code = modification.modified_code.lower()
        for pattern in dangerous_patterns:
            if pattern in code:
                return False
        
        # Check for syntax validity
        try:
            ast.parse(modification.modified_code)
        except SyntaxError:
            return False
        
        # Check for infinite loops (basic detection)
        if 'while True:' in modification.modified_code and 'break' not in modification.modified_code:
            return False
        
        return True
    
    def _generate_modified_organism_code(self, organism, modification: CodeModification) -> str:
        """Generate complete organism code with modifications"""
        
        # Start with base template
        code_lines = [self.template_engine.base_template]
        
        # Add the specific modification
        code_lines.append(f"\n    # Modification: {modification.modification_id}")
        code_lines.append(f"    # Type: {modification.modification_type.value}")
        code_lines.append(f"    # Reason: {modification.reason}")
        code_lines.append(modification.modified_code)
        
        # Add organism-specific data preservation
        code_lines.append(f'''
    def save_state(self):
        """Save organism state for persistence"""
        return {{
            'id': self.id,
            'generation': self.generation,
            'age': self.age,
            'energy': self.energy,
            'capabilities': [cap.value for cap in self.capabilities],
            'code_modifications': [mod.__dict__ for mod in self.code_modifications],
            'code_version': self.code_version
        }}
    
    def load_state(self, state_data):
        """Load organism state from persistence"""
        for key, value in state_data.items():
            if key != 'code_modifications':
                setattr(self, key, value)
''')
        
        return '\n'.join(code_lines)
    
    def _save_organism_code(self, organism, code: str) -> str:
        """Save organism code to file for persistence"""
        
        filename = f"organism_{organism.id}_v{getattr(organism, 'code_version', 1)}.py"
        filepath = os.path.join(self.temp_code_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        return filepath
    
    def _inject_modification_into_organism(self, organism, modification: CodeModification):
        """Inject modification into living organism"""
        
        # This is a simplified injection - in a full system, you'd dynamically
        # create new methods and replace them in the organism instance
        
        if modification.modification_type == ModificationType.CAPABILITY_ADDITION:
            # Add new method to organism
            method_name = modification.target_method
            
            # Create a simple version of the new capability
            if method_name == "learn_from_peer":
                def learn_from_peer(peer_organism):
                    organism.social_interactions += 1
                    if hasattr(peer_organism, 'successful_strategies'):
                        organism.traits.learning_rate *= 1.02
                    return True
                
                setattr(organism, method_name, learn_from_peer)
        
        elif modification.modification_type == ModificationType.EFFICIENCY_IMPROVEMENT:
            # Modify existing behavior
            if "metabolism" in modification.target_method.lower():
                # Improve energy efficiency
                organism.energy_efficiency *= 1.2
            elif "food_finding" in modification.target_method.lower():
                # Improve food finding
                if not hasattr(organism, 'enhanced_food_finding'):
                    organism.enhanced_food_finding = True
    
    def inherit_modifications(self, parent_organism, child_organism) -> int:
        """Inherit code modifications from parent to child"""
        
        if not hasattr(parent_organism, 'code_modifications'):
            return 0
        
        inherited_count = 0
        child_organism.code_modifications = []
        
        for modification in parent_organism.code_modifications:
            # 80% chance to inherit each modification
            if random.random() < 0.8:
                # Create inherited modification
                inherited_mod = CodeModification(
                    modification_id=modification.modification_id + "_inherited",
                    modification_type=modification.modification_type,
                    target_method=modification.target_method,
                    original_code=modification.original_code,
                    modified_code=modification.modified_code,
                    reason=f"Inherited from parent: {modification.reason}",
                    created_by="inheritance",
                    timestamp=time.time(),
                    success_rate=modification.success_rate * 0.9  # Slight degradation
                )
                
                # Apply to child
                if self.apply_modification_to_organism(child_organism, inherited_mod):
                    inherited_count += 1
                    modification.inheritance_count += 1
        
        return inherited_count
    
    def get_modification_statistics(self) -> Dict:
        """Get statistics about all modifications"""
        
        stats = {
            'total_modifications': len(self.modification_history),
            'modifications_by_type': {},
            'average_success_rate': 0.0,
            'total_inheritances': 0
        }
        
        for mod in self.modification_history:
            mod_type = mod.modification_type.value
            if mod_type not in stats['modifications_by_type']:
                stats['modifications_by_type'][mod_type] = 0
            stats['modifications_by_type'][mod_type] += 1
            stats['total_inheritances'] += mod.inheritance_count
        
        if self.modification_history:
            stats['average_success_rate'] = sum(mod.success_rate for mod in self.modification_history) / len(self.modification_history)
        
        return stats

class TeacherCodeModifier:
    """Teacher/Parent that can modify organism code based on analysis"""
    
    def __init__(self):
        self.modification_engine = CodeModificationEngine()
        self.teaching_budget = 5  # Can modify 5 organisms per day
        self.used_budget = 0
        self.last_reset = time.time()
        
    def analyze_and_modify_organism(self, organism, force_modification=False) -> bool:
        """Analyze organism and apply beneficial modifications"""
        
        self.reset_budget_if_needed()
        
        if not force_modification and self.used_budget >= self.teaching_budget:
            return False
        
        # Analyze organism for potential improvements
        suggestions = self.modification_engine.analyze_organism_for_modifications(organism)
        
        if not suggestions:
            return False
        
        # Choose most beneficial modification
        best_suggestion = suggestions[0]  # Could use more sophisticated selection
        
        # Create modification
        reason = f"Teacher analysis: organism struggling with {best_suggestion}"
        modification = self.modification_engine.create_modification(
            organism, best_suggestion, reason
        )
        
        if modification:
            # Apply modification
            success = self.modification_engine.apply_modification_to_organism(
                organism, modification
            )
            
            if success:
                self.used_budget += 1
                print(f"👨‍🏫 Teacher modified organism {organism.id}")
                return True
        
        return False
    
    def reset_budget_if_needed(self):
        """Reset daily teaching budget"""
        current_time = time.time()
        if current_time - self.last_reset > 3600:  # 1 hour = 1 day in sim
            self.used_budget = 0
            self.last_reset = current_time
    
    def get_teaching_report(self) -> Dict:
        """Get report on teaching activities"""
        return {
            'budget_used': f"{self.used_budget}/{self.teaching_budget}",
            'modification_stats': self.modification_engine.get_modification_statistics()
        }

# Integration functions
def create_code_evolution_system():
    """Create the complete code evolution system"""
    return {
        'modification_engine': CodeModificationEngine(),
        'teacher_modifier': TeacherCodeModifier()
    }

def apply_code_evolution(organism, ecosystem_data, code_evolution_system):
    """Apply code evolution analysis and modifications"""
    
    teacher = code_evolution_system['teacher_modifier']
    
    # Teacher analyzes organism every 50 age units
    if organism.age > 0 and organism.age % 50 == 0:
        if organism.current_fitness < 1.0:  # Only modify struggling organisms
            teacher.analyze_and_modify_organism(organism)
    
    return True

# Example usage
if __name__ == "__main__":
    print("🔧 Testing Code Evolution System...")
    
    # Create code evolution system
    code_evolution_system = create_code_evolution_system()
    
    # Test modification creation
    modifier = code_evolution_system['teacher_modifier']
    engine = code_evolution_system['modification_engine']
    
    # Create a mock organism
    class MockOrganism:
        def __init__(self):
            self.id = "test_001"
            self.age = 100
            self.energy = 25  # Struggling
            self.energy_efficiency = 0.3  # Poor efficiency
            self.social_interactions = 0
            self.failed_attempts = 25
            self.memory = ["data"] * 60  # Memory bloat
            self.current_fitness = 0.4  # Low fitness
            self.capabilities = set()
            self.traits = type('obj', (object,), {'learning_rate': 0.1})
    
    organism = MockOrganism()
    
    # Analyze and modify
    success = modifier.analyze_and_modify_organism(organism, force_modification=True)
    print(f"Modification success: {success}")
    
    # Show teaching report
    report = modifier.get_teaching_report()
    print(f"Teaching report: {report}")
    
    print("✅ Code evolution system ready!")