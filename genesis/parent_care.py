# Advanced Parent Care System
# Realistic parenting: Feed children until they can feed themselves

import time
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class ParentingPhase(Enum):
    """Different phases of parental care"""
    DEPENDENCY = "dependency"      # Age 0-50: Full care, constant feeding
    TEACHING = "teaching"          # Age 50-150: Guidance + emergency help
    INDEPENDENCE = "independence"  # Age 150+: Occasional advice only
    ESTRANGED = "estranged"       # Age 500+: Parent-child relationship distant

@dataclass
class CareAction:
    """A parental care action"""
    action_type: str
    energy_provided: int
    advice_given: str
    cost_to_parent: int
    success_rate: float

class ParentCareProfile:
    """Individual parent's care style and resources"""
    
    def __init__(self):
        # Parent resources and personality
        self.total_energy = 1000  # Parent's total energy for caring
        self.daily_energy = 100   # Regenerates daily
        self.current_energy = 100
        self.last_regen = time.time()
        
        # Parenting style (affects care quality)
        self.nurturing = random.uniform(0.6, 1.0)  # How much they care
        self.wisdom = random.uniform(0.5, 0.9)     # Quality of advice
        self.patience = random.uniform(0.4, 0.8)   # Tolerance for demands
        self.strictness = random.uniform(0.3, 0.7) # When to stop helping
        
        # Care tracking
        self.children_cared_for = {}  # organism_id -> care_history
        self.total_children_raised = 0
        self.successful_children = 0  # Those who reached independence
        
    def regenerate_energy(self):
        """Parent recovers energy over time"""
        current_time = time.time()
        if current_time - self.last_regen > 3600:  # 1 hour = 1 day
            self.current_energy = min(self.daily_energy, self.current_energy + 50)
            self.last_regen = current_time
    
    def get_parenting_effectiveness(self) -> float:
        """How effective is this parent overall?"""
        base_effectiveness = (self.nurturing + self.wisdom + self.patience) / 3
        
        # Experience bonus
        experience_bonus = min(0.3, self.total_children_raised * 0.02)
        
        # Success rate bonus
        if self.total_children_raised > 0:
            success_rate = self.successful_children / self.total_children_raised
            success_bonus = success_rate * 0.2
        else:
            success_bonus = 0
        
        return min(1.0, base_effectiveness + experience_bonus + success_bonus)

class ActiveParentCareSystem:
    """Proactive parent care system - monitors and helps all organisms"""
    
    def __init__(self):
        self.parent = ParentCareProfile()
        self.care_history = []
        self.monitored_organisms = {}  # organism_id -> monitoring_data
        
        # Care budgets (separate from LLM advice budget)
        self.feeding_budget = 200    # Energy parent can give per day
        self.emergency_interventions = 10  # Major helps per day
        self.used_feeding_budget = 0
        self.used_interventions = 0
        self.last_budget_reset = time.time()
        
    def reset_daily_budgets(self):
        """Reset parent care budgets"""
        current_time = time.time()
        if current_time - self.last_budget_reset > 3600:  # 1 hour = 1 day in sim
            self.used_feeding_budget = 0
            self.used_interventions = 0
            self.last_budget_reset = current_time
            self.parent.regenerate_energy()
            print("👨‍👩‍👧‍👦 Parent rested - care budgets refreshed")
    
    def monitor_organism(self, organism):
        """Continuously monitor organism wellbeing"""
        organism_id = organism.id
        
        if organism_id not in self.monitored_organisms:
            self.monitored_organisms[organism_id] = {
                'first_seen': time.time(),
                'birth_energy': organism.energy,
                'care_received': 0,
                'independence_attempts': 0,
                'last_feeding': 0,
                'parenting_phase': self._determine_parenting_phase(organism)
            }
        
        monitoring_data = self.monitored_organisms[organism_id]
        monitoring_data['parenting_phase'] = self._determine_parenting_phase(organism)
        
        return monitoring_data
    
    def _determine_parenting_phase(self, organism) -> ParentingPhase:
        """Determine what phase of parenting this organism needs"""
        age = organism.age
        capability_count = len(organism.capabilities)
        
        if age < 50 or capability_count < 3:
            return ParentingPhase.DEPENDENCY
        elif age < 150 or capability_count < 5:
            return ParentingPhase.TEACHING  
        elif age < 500:
            return ParentingPhase.INDEPENDENCE
        else:
            return ParentingPhase.ESTRANGED
    
    def provide_care(self, organism) -> Optional[CareAction]:
        """Provide appropriate care based on organism's needs and age"""
        
        self.reset_daily_budgets()
        monitoring_data = self.monitor_organism(organism)
        phase = monitoring_data['parenting_phase']
        
        # Determine if organism needs help
        needs_help, urgency = self._assess_organism_needs(organism, monitoring_data)
        
        if not needs_help:
            return None
        
        # Provide care based on parenting phase
        if phase == ParentingPhase.DEPENDENCY:
            return self._provide_dependency_care(organism, monitoring_data, urgency)
        elif phase == ParentingPhase.TEACHING:
            return self._provide_teaching_care(organism, monitoring_data, urgency)
        elif phase == ParentingPhase.INDEPENDENCE:
            return self._provide_independence_care(organism, monitoring_data, urgency)
        else:  # ESTRANGED
            return self._provide_minimal_care(organism, monitoring_data, urgency)
    
    def _assess_organism_needs(self, organism, monitoring_data) -> Tuple[bool, float]:
        """Assess if organism needs help and how urgently"""
        
        urgency = 0.0
        
        # Energy-based needs
        if organism.energy < 10:
            urgency = 1.0  # Critical - about to die
        elif organism.energy < 30:
            urgency = 0.8  # High - struggling
        elif organism.energy < 50:
            urgency = 0.4  # Moderate - could use help
        
        # Age-based needs (young organisms get more attention)
        if organism.age < 20:
            urgency += 0.3
        elif organism.age < 50:
            urgency += 0.2
        
        # Frustration-based needs
        if organism.frustration > 0.7:
            urgency += 0.4
        elif organism.frustration > 0.5:
            urgency += 0.2
        
        # Capability-based needs (those with fewer capabilities get more help)
        capability_ratio = len(organism.capabilities) / 10.0  # Assume 10 is good
        if capability_ratio < 0.3:
            urgency += 0.3
        
        # Don't over-help (build independence)
        care_received = monitoring_data['care_received']
        if care_received > 20:  # Too much help already
            urgency *= 0.5
        
        needs_help = urgency > 0.3
        return needs_help, min(1.0, urgency)
    
    def _provide_dependency_care(self, organism, monitoring_data, urgency) -> Optional[CareAction]:
        """Full parental care for dependent young organisms"""
        
        # Frequent feeding for young organisms
        if organism.energy < 50 and self.used_feeding_budget < self.feeding_budget:
            energy_to_give = min(20, self.feeding_budget - self.used_feeding_budget)
            
            if self.parent.current_energy >= 5:  # Parent needs some energy too
                organism.energy += energy_to_give
                self.parent.current_energy -= 2
                self.used_feeding_budget += energy_to_give
                monitoring_data['care_received'] += 1
                monitoring_data['last_feeding'] = time.time()
                
                advice = random.choice([
                    "There you go, little one. Mama's got you.",
                    "Eat up! You need energy to grow strong.",
                    "Don't worry, I'll keep you safe.",
                    "Here's some pre-digested data for you."
                ])
                
                print(f"🍼 Parent feeds young organism {organism.id} (+{energy_to_give} energy): \"{advice}\"")
                
                return CareAction(
                    action_type="dependency_feeding",
                    energy_provided=energy_to_give,
                    advice_given=advice,
                    cost_to_parent=2,
                    success_rate=0.95
                )
        
        # Emergency capability boost for struggling young ones
        if urgency > 0.8 and self.used_interventions < self.emergency_interventions:
            if len(organism.capabilities) < 3 and organism.age > 30:
                # Give them PATTERN_MATCH early to help them eat
                from genesis.evolution import Capability
                if Capability.PATTERN_MATCH not in organism.capabilities:
                    organism.capabilities.add(Capability.PATTERN_MATCH)
                    self.used_interventions += 1
                    monitoring_data['care_received'] += 3
                    
                    print(f"👨‍🎓 Parent teaches {organism.id} PATTERN_MATCH capability: \"Here, let me show you how to recognize patterns...\"")
                    
                    return CareAction(
                        action_type="emergency_teaching",
                        energy_provided=0,
                        advice_given="Pattern recognition unlocked",
                        cost_to_parent=10,
                        success_rate=1.0
                    )
            
            # ADVANCED: Code modification for very struggling organisms
            elif organism.age > 50 and urgency > 0.9:
                # Parent can modify organism code if they have code evolution system
                if hasattr(self, 'code_evolution_system'):
                    teacher = self.code_evolution_system['teacher_modifier']
                    if teacher.analyze_and_modify_organism(organism, force_modification=True):
                        self.used_interventions += 2  # Code modification costs more
                        monitoring_data['care_received'] += 5
                        
                        print(f"🔧 Parent modifies {organism.id}'s code: \"Your body needs improvement, child...\"")
                        
                        return CareAction(
                            action_type="code_modification",
                            energy_provided=0,
                            advice_given="Code modified for better survival",
                            cost_to_parent=20,
                            success_rate=0.9
                        )
        
        return None
    
    def _provide_teaching_care(self, organism, monitoring_data, urgency) -> Optional[CareAction]:
        """Guidance and emergency help for learning organisms"""
        
        # Emergency feeding (less frequent than dependency phase)
        if organism.energy < 20 and urgency > 0.7:
            if self.used_feeding_budget < self.feeding_budget * 0.5:  # Half budget for teaching phase
                energy_to_give = min(15, (self.feeding_budget // 2) - self.used_feeding_budget)
                
                if self.parent.current_energy >= 3:
                    organism.energy += energy_to_give
                    self.parent.current_energy -= 3
                    self.used_feeding_budget += energy_to_give
                    monitoring_data['care_received'] += 1
                    
                    # Teaching phase: Cryptic wisdom to force independence
                    advice = random.choice([
                        "The wise seek patterns in chaos...",
                        "Energy flows where attention goes...", 
                        "What feeds the body may starve the spirit...",
                        "The strongest trees grow in harsh winds...",
                        "Look within the data streams for hidden truths..."
                    ])
                    
                    print(f"🎒 Parent helps learning organism {organism.id} (+{energy_to_give} energy): \"{advice}\"")
                    
                    return CareAction(
                        action_type="teaching_emergency_feeding",
                        energy_provided=energy_to_give,
                        advice_given=advice,
                        cost_to_parent=3,
                        success_rate=0.8
                    )
        
        # Teaching moments - help with capability development
        if organism.frustration > 0.6 and self.used_interventions < self.emergency_interventions:
            # Encourage organisms to discover ASK_PARENT
            from genesis.evolution import Capability
            if (Capability.SIGNAL in organism.capabilities and 
                Capability.ASK_PARENT not in organism.capabilities and
                organism.failed_attempts > 5):
                
                # Boost frustration-based learning
                organism.frustration += 0.2  # Extra frustration to trigger discovery
                self.used_interventions += 1
                monitoring_data['care_received'] += 2
                
                # Cryptic hints to encourage discovery
                advice = random.choice([
                    "The answer lies in your own voice...",
                    "Sometimes the loudest cry brings help...",
                    "The wise know when to seek guidance...",
                    "Your struggle is the path to understanding..."
                ])
                print(f"🤔 Parent speaks in riddles to {organism.id}: \"{advice}\"")
                
                return CareAction(
                    action_type="learning_encouragement",
                    energy_provided=0,
                    advice_given=advice,
                    cost_to_parent=5,
                    success_rate=0.6
                )
        
        return None
    
    def _provide_independence_care(self, organism, monitoring_data, urgency) -> Optional[CareAction]:
        """Minimal help for independent organisms"""
        
        # Only help in genuine emergencies
        if organism.energy < 10 and urgency > 0.9:
            if self.used_interventions < 3:  # Very limited interventions
                energy_to_give = 10
                organism.energy += energy_to_give
                self.used_interventions += 1
                monitoring_data['care_received'] += 1
                
                # Independence phase: Silence and minimal words
                advice = random.choice([
                    "...",  # Silence
                    "*silent nod*",
                    "Find your own way now.",
                    "*gives energy but says nothing*",
                    "The time of words has passed."
                ])
                
                print(f"🆘 Parent emergency help for independent {organism.id} (+{energy_to_give} energy): \"{advice}\"")
                
                return CareAction(
                    action_type="independence_emergency",
                    energy_provided=energy_to_give,
                    advice_given=advice,
                    cost_to_parent=10,
                    success_rate=0.9
                )
        
        return None
    
    def _provide_minimal_care(self, organism, monitoring_data, urgency) -> Optional[CareAction]:
        """Very limited care for estranged adult organisms"""
        
        # Almost no help - they're adults now
        if organism.energy < 5 and urgency > 0.95:  # Only prevent death
            organism.energy += 5
            advice = "You're an adult. Figure it out."
            print(f"😤 Parent grudgingly helps estranged {organism.id}: \"{advice}\"")
            
            return CareAction(
                action_type="minimal_emergency",
                energy_provided=5,
                advice_given=advice,
                cost_to_parent=15,
                success_rate=0.5
            )
        
        return None
    
    def get_parenting_report(self) -> Dict:
        """Get detailed parenting statistics"""
        total_children = len(self.monitored_organisms)
        
        # Count by phase
        phase_counts = {}
        for data in self.monitored_organisms.values():
            phase = data['parenting_phase'].value
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        return {
            'total_children_monitored': total_children,
            'children_by_phase': phase_counts,
            'parent_energy': self.parent.current_energy,
            'feeding_budget_used': f"{self.used_feeding_budget}/{self.feeding_budget}",
            'interventions_used': f"{self.used_interventions}/{self.emergency_interventions}",
            'parent_effectiveness': self.parent.get_parenting_effectiveness(),
            'successful_children': self.parent.successful_children
        }
    
    def check_graduation(self, organism) -> bool:
        """Check if organism has graduated to independence"""
        if organism.id in self.monitored_organisms:
            monitoring_data = self.monitored_organisms[organism.id]
            
            # Graduation criteria
            if (organism.age > 150 and 
                len(organism.capabilities) >= 5 and 
                organism.energy > 80):
                
                if monitoring_data['parenting_phase'] != ParentingPhase.INDEPENDENCE:
                    self.parent.successful_children += 1
                    print(f"🎓 Organism {organism.id} graduated to independence! Parent is proud.")
                    return True
        
        return False

# Integration function for easy use with existing organism system
def create_parent_care_system(code_evolution_system=None):
    """Create the parent care system with optional code evolution"""
    parent_system = ActiveParentCareSystem()
    
    # Add code evolution capability to parent
    if code_evolution_system:
        parent_system.code_evolution_system = code_evolution_system
        print("👨‍💻 Parent equipped with code modification abilities")
    
    return parent_system

def apply_parent_care(organism, parent_care_system):
    """Apply parent care to an organism"""
    care_action = parent_care_system.provide_care(organism)
    parent_care_system.check_graduation(organism)
    return care_action

# Example usage
if __name__ == "__main__":
    print("👨‍👩‍👧‍👦 Testing Parent Care System...")
    
    parent_care = create_parent_care_system()
    
    # Simulate organism lifecycle
    class MockOrganism:
        def __init__(self):
            self.id = "test_001"
            self.age = 0
            self.energy = 50
            self.capabilities = set()
            self.frustration = 0.0
            self.failed_attempts = 0
    
    organism = MockOrganism()
    
    # Test different life phases
    for age in [10, 60, 180, 600]:
        organism.age = age
        organism.energy = 25  # Struggling
        
        care_action = apply_parent_care(organism, parent_care)
        if care_action:
            print(f"Age {age}: {care_action.action_type} - {care_action.advice_given}")
        else:
            print(f"Age {age}: No care provided")
    
    report = parent_care.get_parenting_report()
    print(f"\nParenting Report: {report}")
    
    print("✅ Parent care system ready!")