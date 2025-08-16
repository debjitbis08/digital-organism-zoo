# Community Activities System
# Shows what organisms actually accomplish together

import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ActivityType(Enum):
    """Types of meaningful activities organisms can perform"""
    KNOWLEDGE_SHARING = "knowledge_sharing"      # Share insights with community
    COLLECTIVE_PROBLEM_SOLVING = "problem_solving"  # Work together on challenges
    RESOURCE_OPTIMIZATION = "resource_optimization"  # Improve food efficiency
    INNOVATION = "innovation"                    # Create new solutions
    TEACHING = "teaching"                        # Help less experienced organisms
    RESEARCH = "research"                        # Investigate patterns in data
    COMMUNITY_BUILDING = "community_building"    # Strengthen social bonds
    CRISIS_RESPONSE = "crisis_response"          # Emergency community actions

@dataclass
class CommunityActivity:
    """A meaningful activity performed by organisms"""
    activity_type: ActivityType
    participants: List[str]  # organism IDs
    description: str
    impact_score: float
    timestamp: float
    energy_cost: int
    knowledge_generated: Optional[str] = None
    community_benefit: float = 0.0

class CommunityActivitySystem:
    """Manages and tracks meaningful community activities"""
    
    def __init__(self):
        self.completed_activities: List[CommunityActivity] = []
        self.active_projects: Dict[str, Dict] = {}
        self.community_knowledge_pool: Dict[str, Any] = {}
        self.crisis_response_active = False
        
    def check_for_activities(self, organisms: List, ecosystem_stats: Dict) -> List[CommunityActivity]:
        """Check if organisms can perform meaningful activities"""
        
        activities = []
        
        # Knowledge sharing between organisms
        knowledge_activities = self._check_knowledge_sharing(organisms)
        activities.extend(knowledge_activities)
        
        # Collective problem solving
        problem_solving = self._check_problem_solving(organisms, ecosystem_stats)
        if problem_solving:
            activities.append(problem_solving)
        
        # Resource optimization
        optimization = self._check_resource_optimization(organisms, ecosystem_stats)
        if optimization:
            activities.append(optimization)
        
        # Innovation projects
        innovation = self._check_innovation_projects(organisms)
        if innovation:
            activities.append(innovation)
        
        # Teaching activities
        teaching = self._check_teaching_activities(organisms)
        activities.extend(teaching)
        
        # Crisis response
        crisis_response = self._check_crisis_response(organisms, ecosystem_stats)
        if crisis_response:
            activities.append(crisis_response)
        
        # Execute activities and track them
        for activity in activities:
            self._execute_activity(activity, organisms)
            self.completed_activities.append(activity)
        
        return activities
    
    def _check_knowledge_sharing(self, organisms: List) -> List[CommunityActivity]:
        """Check for knowledge sharing opportunities"""
        activities = []
        
        # Find organisms with knowledge to share
        knowledgeable_organisms = []
        learning_organisms = []
        
        for organism in organisms:
            if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
                summary = organism.knowledge_base.get_knowledge_summary()
                if summary['total_insights'] >= 5:
                    knowledgeable_organisms.append(organism)
                elif summary['total_insights'] < 3:
                    learning_organisms.append(organism)
        
        # Create knowledge sharing activities
        if knowledgeable_organisms and learning_organisms:
            for teacher in knowledgeable_organisms[:2]:  # Limit to 2 teachers
                if teacher.energy > 30 and random.random() < 0.3:  # 30% chance
                    students = random.sample(learning_organisms, min(2, len(learning_organisms)))
                    
                    # Determine what knowledge to share
                    if hasattr(teacher.knowledge_base, 'knowledge_items') and teacher.knowledge_base.knowledge_items:
                        recent_insight = teacher.knowledge_base.knowledge_items[-1]
                        shared_knowledge = recent_insight.content
                    else:
                        shared_knowledge = "general experience"
                    
                    activity = CommunityActivity(
                        activity_type=ActivityType.KNOWLEDGE_SHARING,
                        participants=[teacher.id] + [s.id for s in students],
                        description=f"Organism {teacher.id} shares '{shared_knowledge}' with {len(students)} learners",
                        impact_score=0.7,
                        timestamp=time.time(),
                        energy_cost=5,
                        knowledge_generated=shared_knowledge,
                        community_benefit=0.2 * len(students)
                    )
                    activities.append(activity)
        
        return activities
    
    def _check_problem_solving(self, organisms: List, ecosystem_stats: Dict) -> Optional[CommunityActivity]:
        """Check for collective problem solving opportunities"""
        
        # Identify community problems
        food_scarcity = ecosystem_stats.get('food_scarcity', 1.0) < 0.5
        high_failure_rate = sum(getattr(org, 'failed_attempts', 0) for org in organisms) > len(organisms) * 20
        
        if food_scarcity or high_failure_rate:
            # Find problem solvers
            capable_organisms = []
            for organism in organisms:
                if (hasattr(organism, '_behavior_modifiers') and 
                    organism._behavior_modifiers.get('tech_awareness', 0) > 0.3 and 
                    organism.energy > 40):
                    capable_organisms.append(organism)
            
            if len(capable_organisms) >= 2:
                problem = "food scarcity" if food_scarcity else "high failure rates"
                
                return CommunityActivity(
                    activity_type=ActivityType.COLLECTIVE_PROBLEM_SOLVING,
                    participants=[org.id for org in capable_organisms[:3]],
                    description=f"Collaborative problem solving: addressing {problem}",
                    impact_score=1.0,
                    timestamp=time.time(),
                    energy_cost=15,
                    community_benefit=0.8
                )
        
        return None
    
    def _check_resource_optimization(self, organisms: List, ecosystem_stats: Dict) -> Optional[CommunityActivity]:
        """Check for resource optimization activities"""
        
        # Find efficient organisms who can optimize resource use
        efficient_organisms = []
        for organism in organisms:
            if (hasattr(organism.traits, 'efficiency') and 
                organism.traits.efficiency > 0.7 and 
                organism.energy > 35):
                efficient_organisms.append(organism)
        
        # If we have efficient organisms and resource challenges
        if (len(efficient_organisms) >= 2 and 
            ecosystem_stats.get('total_food_available', 0) < 50):
            
            return CommunityActivity(
                activity_type=ActivityType.RESOURCE_OPTIMIZATION,
                participants=[org.id for org in efficient_organisms[:2]],
                description="Optimizing community resource usage and food distribution",
                impact_score=0.8,
                timestamp=time.time(),
                energy_cost=10,
                community_benefit=0.5
            )
        
        return None
    
    def _check_innovation_projects(self, organisms: List) -> Optional[CommunityActivity]:
        """Check for innovation projects"""
        
        # Find creative organisms
        creative_organisms = []
        for organism in organisms:
            if (hasattr(organism.traits, 'creativity') and 
                organism.traits.creativity > 0.4 and 
                hasattr(organism, '_behavior_modifiers') and
                organism._behavior_modifiers.get('code_affinity', 0) > 0.2):
                creative_organisms.append(organism)
        
        if len(creative_organisms) >= 2 and random.random() < 0.2:  # 20% chance
            return CommunityActivity(
                activity_type=ActivityType.INNOVATION,
                participants=[org.id for org in creative_organisms[:2]],
                description="Developing new approaches to data processing and foraging",
                impact_score=1.2,
                timestamp=time.time(),
                energy_cost=20,
                knowledge_generated="innovative_technique",
                community_benefit=0.3
            )
        
        return None
    
    def _check_teaching_activities(self, organisms: List) -> List[CommunityActivity]:
        """Check for teaching activities"""
        activities = []
        
        # Find organisms that want to teach
        for organism in organisms:
            if (hasattr(organism, 'knowledge_base') and 
                organism.knowledge_base and
                organism.knowledge_base.get_knowledge_summary()['total_insights'] >= 10 and
                organism.energy > 25):
                
                # Find students
                students = []
                for other in organisms:
                    if (other.id != organism.id and 
                        other.age < organism.age and 
                        len(other.capabilities) < len(organism.capabilities)):
                        students.append(other)
                
                if students and random.random() < 0.25:  # 25% chance
                    student = random.choice(students)
                    
                    activity = CommunityActivity(
                        activity_type=ActivityType.TEACHING,
                        participants=[organism.id, student.id],
                        description=f"Organism {organism.id} mentors organism {student.id}",
                        impact_score=0.6,
                        timestamp=time.time(),
                        energy_cost=8,
                        community_benefit=0.4
                    )
                    activities.append(activity)
        
        return activities
    
    def _check_crisis_response(self, organisms: List, ecosystem_stats: Dict) -> Optional[CommunityActivity]:
        """Check for crisis response activities"""
        
        # Detect crisis conditions
        avg_energy = sum(org.energy for org in organisms) / len(organisms)
        crisis_organisms = sum(1 for org in organisms if org.energy < 20)
        
        if avg_energy < 30 or crisis_organisms >= len(organisms) * 0.6:
            # Emergency community response
            healthy_organisms = [org for org in organisms if org.energy > 40]
            
            if healthy_organisms:
                return CommunityActivity(
                    activity_type=ActivityType.CRISIS_RESPONSE,
                    participants=[org.id for org in healthy_organisms],
                    description=f"Emergency response: {len(healthy_organisms)} organisms coordinating crisis aid",
                    impact_score=1.5,
                    timestamp=time.time(),
                    energy_cost=25,
                    community_benefit=1.0
                )
        
        return None
    
    def _execute_activity(self, activity: CommunityActivity, organisms: List):
        """Execute the activity and apply its effects"""
        
        participant_organisms = [org for org in organisms if org.id in activity.participants]
        
        # Apply energy costs
        energy_per_participant = activity.energy_cost // len(participant_organisms)
        for organism in participant_organisms:
            organism.energy = max(5, organism.energy - energy_per_participant)
        
        # Apply benefits based on activity type
        if activity.activity_type == ActivityType.KNOWLEDGE_SHARING:
            # Transfer some knowledge
            if len(participant_organisms) > 1:
                teacher = participant_organisms[0]
                students = participant_organisms[1:]
                
                if hasattr(teacher, 'knowledge_base') and teacher.knowledge_base:
                    for student in students:
                        if not hasattr(student, 'knowledge_base'):
                            from genesis.data_processor import OrganismKnowledgeBase
                            student.knowledge_base = OrganismKnowledgeBase()
                        
                        # Simulate knowledge transfer
                        student.social_interactions += 1
                        if hasattr(student.traits, 'learning_rate'):
                            student.traits.learning_rate *= 1.05  # Small learning boost
        
        elif activity.activity_type == ActivityType.COLLECTIVE_PROBLEM_SOLVING:
            # Improve community problem-solving capabilities
            for organism in participant_organisms:
                if hasattr(organism.traits, 'cooperation'):
                    organism.traits.cooperation = min(1.0, organism.traits.cooperation + 0.1)
                organism.social_interactions += 2
        
        elif activity.activity_type == ActivityType.RESOURCE_OPTIMIZATION:
            # Improve efficiency for all participants
            for organism in participant_organisms:
                if hasattr(organism.traits, 'efficiency'):
                    organism.traits.efficiency = min(1.0, organism.traits.efficiency + 0.05)
        
        elif activity.activity_type == ActivityType.INNOVATION:
            # Boost creativity and risk-taking
            for organism in participant_organisms:
                if hasattr(organism.traits, 'creativity'):
                    organism.traits.creativity = min(1.0, organism.traits.creativity + 0.1)
                if hasattr(organism.traits, 'risk_taking'):
                    organism.traits.risk_taking = min(1.0, organism.traits.risk_taking + 0.05)
        
        elif activity.activity_type == ActivityType.CRISIS_RESPONSE:
            # Provide emergency energy to struggling organisms
            struggling = [org for org in organisms if org.energy < 25]
            if struggling:
                energy_donation = min(5, len(participant_organisms) * 3)
                for organism in struggling[:3]:  # Help up to 3 struggling organisms
                    organism.energy += energy_donation
        
        # Add to community knowledge pool
        if activity.knowledge_generated:
            if activity.knowledge_generated not in self.community_knowledge_pool:
                self.community_knowledge_pool[activity.knowledge_generated] = {
                    'created_at': time.time(),
                    'contributors': activity.participants,
                    'applications': 0
                }
    
    def get_community_stats(self) -> Dict:
        """Get statistics about community activities"""
        
        if not self.completed_activities:
            return {
                "status": "no_activities", 
                "total_activities": 0,
                "recent_activities": 0,
                "activity_types": {},
                "total_impact": 0.0,
                "community_benefit": 0.0,
                "knowledge_pool_size": 0,
                "most_active_type": None
            }
        
        recent_activities = [a for a in self.completed_activities if time.time() - a.timestamp < 3600]
        
        activity_counts = {}
        for activity in self.completed_activities:
            activity_type = activity.activity_type.value
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        
        total_impact = sum(a.impact_score for a in self.completed_activities)
        total_community_benefit = sum(a.community_benefit for a in self.completed_activities)
        
        return {
            "total_activities": len(self.completed_activities),
            "recent_activities": len(recent_activities),
            "activity_types": activity_counts,
            "total_impact": total_impact,
            "community_benefit": total_community_benefit,
            "knowledge_pool_size": len(self.community_knowledge_pool),
            "most_active_type": max(activity_counts.items(), key=lambda x: x[1])[0] if activity_counts else None
        }
    
    def print_recent_activities(self, hours: int = 1):
        """Print recent community activities"""
        
        cutoff = time.time() - (hours * 3600)
        recent = [a for a in self.completed_activities if a.timestamp > cutoff]
        
        if not recent:
            print(f"📊 No community activities in the last {hours} hour(s)")
            return
        
        print(f"\n🌟 COMMUNITY ACTIVITIES (Last {hours} hour(s))")
        print("=" * 50)
        
        for activity in recent[-5:]:  # Show last 5
            participants_str = f"{len(activity.participants)} organisms"
            print(f"🎯 {activity.activity_type.value.replace('_', ' ').title()}")
            print(f"   {activity.description}")
            print(f"   Participants: {participants_str}, Impact: {activity.impact_score:.1f}")
            if activity.knowledge_generated:
                print(f"   Knowledge: {activity.knowledge_generated}")
            print()

# Integration function
def create_community_system():
    """Create the community activity system"""
    return CommunityActivitySystem()

def check_community_activities(organisms: List, ecosystem_stats: Dict, community_system):
    """Check and execute community activities"""
    
    if not community_system:
        return []
    
    activities = community_system.check_for_activities(organisms, ecosystem_stats)
    
    # Print activities as they happen
    for activity in activities:
        participants_str = f"{len(activity.participants)} organisms"
        print(f"🎯 COMMUNITY: {activity.description} ({participants_str})")
    
    return activities