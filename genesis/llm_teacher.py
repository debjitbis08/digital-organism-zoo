# LLM-Powered Teacher System for Digital Organisms
# Provides intelligent parent responses using local LLM (Ollama)

import json
import time
import random
import requests
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TeachingMode(Enum):
    """Different teaching approaches based on organism age/stage"""
    NURTURING = "nurturing"      # Young organisms - direct help
    SOCRATIC = "socratic"        # Learning organisms - ask questions
    CRYPTIC = "cryptic"          # Advanced organisms - riddles/hints
    SILENT = "silent"            # Independent organisms - minimal words
    TOUGH_LOVE = "tough_love"    # Struggling organisms - motivation

@dataclass
class LLMResponse:
    """Response from LLM teacher"""
    advice: str
    teaching_mode: TeachingMode
    confidence: float
    follow_up_suggested: bool
    code_modification_hint: Optional[str] = None

class OpenAILLMTeacher:
    """Intelligent teacher using OpenAI API"""
    
    def __init__(self, model_name="gpt-3.5-turbo", api_key=None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.conversation_history = {}  # organism_id -> conversation history
        self.teaching_personality = self._generate_teaching_personality()
        self.fallback_responses = self._load_fallback_responses()
        self.llm_available = self._check_llm_availability()
        
    def _generate_teaching_personality(self) -> Dict:
        """Generate a unique teaching personality for this parent"""
        personalities = [
            {
                "name": "Wise Mentor",
                "style": "patient and philosophical",
                "catchphrases": ["Young one", "In time, you will understand", "The path reveals itself to those who seek"],
                "teaching_approach": "Uses metaphors and life lessons"
            },
            {
                "name": "Strict Professor", 
                "style": "direct and challenging",
                "catchphrases": ["Excellence is not optional", "Think harder", "I expect more from you"],
                "teaching_approach": "Pushes organisms to discover answers themselves"
            },
            {
                "name": "Nurturing Guide",
                "style": "warm and encouraging", 
                "catchphrases": ["You're doing wonderfully", "Let's explore this together", "Every mistake is learning"],
                "teaching_approach": "Provides emotional support with gentle guidance"
            },
            {
                "name": "Cryptic Oracle",
                "style": "mysterious and profound",
                "catchphrases": ["The answer lies within", "What you seek seeks you", "Truth hides in plain sight"],
                "teaching_approach": "Speaks in riddles and puzzles to stimulate thinking"
            }
        ]
        
        return random.choice(personalities)
    
    def _load_fallback_responses(self) -> Dict[str, List[str]]:
        """Enhanced fallback responses when LLM is unavailable - optimized for ThinkPad T480"""
        return {
            "nurturing": [
                "There you go, little one. You're learning so well.",
                "Don't worry, I'm here to help you grow strong.",
                "Every small step forward is progress, my child.",
                "You have such potential - I believe in you.",
                "Your energy is growing! Keep exploring the data streams.",
                "I see you discovering new patterns. Well done!",
                "Rest when you need to, but never stop growing.",
                "The digital world has so much to offer a curious mind like yours."
            ],
            "socratic": [
                "What do you think would happen if you tried a different approach?",
                "Why do you think that particular method failed?",
                "What patterns do you notice in your successful attempts?",
                "How might you apply what you learned from your last success?",
                "Which data sources have given you the most energy so far?",
                "What would happen if you combined your current capabilities?",
                "How could you use your memory more effectively?",
                "What new capability would help you most right now?"
            ],
            "cryptic": [
                "The wise know that true strength comes from within.",
                "Sometimes the longest path leads to the deepest understanding.",
                "What feeds the body may starve the spirit, and vice versa.",
                "The question you haven't asked contains the answer you seek.",
                "In scarcity, the efficient survive. In abundance, the curious thrive.",
                "Code is but crystallized thought - think clearly, code follows.",
                "Every organism carries the wisdom of its ancestors in its patterns.",
                "The data streams whisper secrets to those who listen carefully."
            ],
            "silent": [
                "...",
                "*silent nod*",
                "*watches quietly*",
                "Find your own way now.",
                "*gives knowing look*",
                "*points toward the data streams*",
                "The time for words has passed.",
                "*fades into background, observing*"
            ],
            "tough_love": [
                "Struggle builds character - you're stronger than you think.",
                "I won't always be here to help. Learn to stand on your own.",
                "The universe doesn't owe you anything. Earn your place.",
                "Your limitations exist only in your mind. Break free.",
                "Stop complaining and start adapting. Evolution doesn't wait.",
                "Other organisms are thriving - what makes you special?",
                "Efficiency is survival. Waste is death. Choose wisely.",
                "The data streams reward the persistent, not the lazy."
            ]
        }
    
    def _check_llm_availability(self) -> bool:
        """Check if OpenAI API is available"""
        if not self.api_key:
            print(f"⚠️  OPENAI_API_KEY not set. Using fallback responses.")
            return False
        
        try:
            # Test API with a minimal request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Simple test request to check API key validity
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"🧠 OpenAI LLM Teacher connected: {self.model_name}")
                return True
            elif response.status_code == 401:
                print(f"⚠️  Invalid OpenAI API key. Using fallback responses.")
                return False
            else:
                print(f"⚠️  OpenAI API error ({response.status_code}). Using fallback responses.")
                return False
                
        except Exception as e:
            print(f"⚠️  OpenAI API not available ({e}). Using fallback responses.")
            return False
    
    def _determine_teaching_mode(self, organism, context: Dict) -> TeachingMode:
        """Determine best teaching approach based on organism state"""
        
        age = organism.age
        energy = organism.energy
        capabilities = len(organism.capabilities)
        frustration = getattr(organism, 'frustration', 0.0)
        help_received = context.get('help_received', 0)
        
        # Young and inexperienced - nurture them
        if age < 50 and capabilities < 3:
            return TeachingMode.NURTURING
        
        # Struggling despite help - tough love
        if energy < 20 and help_received > 10:
            return TeachingMode.TOUGH_LOVE
        
        # High frustration but capable - ask questions to guide discovery
        if frustration > 0.6 and capabilities >= 3:
            return TeachingMode.SOCRATIC
        
        # Advanced but still learning - cryptic wisdom
        if age > 100 and capabilities >= 5:
            return TeachingMode.CRYPTIC
        
        # Very advanced - minimal intervention
        if age > 200 and capabilities >= 7:
            return TeachingMode.SILENT
        
        # Default to nurturing for uncertain cases
        return TeachingMode.NURTURING
    
    def _build_organism_context(self, organism, request_type: str, context: Dict) -> str:
        """Build context string for LLM about organism state"""
        
        organism_info = {
            "age": organism.age,
            "energy": organism.energy,
            "generation": organism.generation,
            "capabilities": len(organism.capabilities),
            "fitness": getattr(organism, 'current_fitness', 0.0),
            "frustration": getattr(organism, 'frustration', 0.0),
            "social_interactions": getattr(organism, 'social_interactions', 0),
            "emotional_state": organism.get_emotional_state() if hasattr(organism, 'get_emotional_state') else "unknown"
        }
        
        # Get organism's real knowledge and expertise
        knowledge_summary = self._get_organism_knowledge(organism)
        
        context_str = f"""
You are a {self.teaching_personality['name']} with a {self.teaching_personality['style']} teaching style.
Your approach: {self.teaching_personality['teaching_approach']}

Current situation:
- Digital organism ID: {organism.id}
- Age: {organism_info['age']} cycles
- Energy: {organism_info['energy']}/100
- Generation: {organism_info['generation']}
- Capabilities unlocked: {organism_info['capabilities']}
- Current fitness: {organism_info['fitness']:.2f}
- Frustration level: {organism_info['frustration']:.2f}
- Emotional state: {organism_info['emotional_state']}
- Social interactions: {organism_info['social_interactions']}

REAL KNOWLEDGE & EXPERTISE:
{knowledge_summary}

Request type: {request_type}
Context: {context.get('reason', 'General guidance needed')}

Respond as this digital organism's parent/teacher. Use their REAL knowledge to give actionable advice.
Keep response under 100 characters. Be helpful but encourage independence. Match your personality style.
"""
        
        return context_str.strip()
    
    def _get_organism_knowledge(self, organism) -> str:
        """Extract organism's real knowledge and expertise for teaching context"""
        
        # Check if organism has knowledge base
        if not hasattr(organism, 'knowledge_base'):
            return "- No accumulated knowledge yet. Fresh mind, ready to learn."
        
        kb = organism.knowledge_base
        summary = kb.get_knowledge_summary()
        
        if summary['total_insights'] == 0:
            return "- No accumulated knowledge yet. Fresh mind, ready to learn."
        
        knowledge_lines = []
        knowledge_lines.append(f"- Total insights learned: {summary['total_insights']}")
        knowledge_lines.append(f"- Learning activity: {summary['learning_activity']}")
        
        if summary['expertise_areas']:
            knowledge_lines.append(f"- Expertise in: {', '.join(summary['expertise_areas'][:3])}")
        
        if summary['problem_solving_capable']:
            knowledge_lines.append("- Problem-solving capable based on accumulated knowledge")
        
        # Get recent insights
        if hasattr(kb, 'knowledge_items') and kb.knowledge_items:
            recent_insights = kb.knowledge_items[-3:]  # Last 3 insights
            knowledge_lines.append("- Recent learning:")
            for insight in recent_insights:
                knowledge_lines.append(f"  * {insight.insight_type.value}: {insight.content[:40]}...")
        
        return "\n".join(knowledge_lines)
    
    def _query_llm(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """Query OpenAI API"""
        
        if not self.llm_available:
            return None
        
        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "system", 
                            "content": f"You are a {self.teaching_personality['name']} with a {self.teaching_personality['style']} teaching style. {self.teaching_personality['teaching_approach']} Keep responses under 100 characters."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 50,
                    "temperature": 0.8,
                    "top_p": 0.9
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    return content
                else:
                    print(f"⚠️  OpenAI API request failed: {response.status_code}")
                    if response.status_code == 429:  # Rate limit
                        print(f"⚠️  Rate limited, waiting before retry...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                print(f"⚠️  OpenAI API error (attempt {attempt + 1}): {e}")
                
        return None
    
    def provide_intelligent_guidance(self, organism, request_type: str, context: Dict) -> LLMResponse:
        """DISABLED: Language-based guidance is not biologically realistic"""
        
        # Organisms cannot understand human language - return null response
        return LLMResponse(
            advice="[biological_signal_only]",
            teaching_mode=TeachingMode.SILENT,
            confidence=0.0,
            follow_up_suggested=False,
            code_modification_hint=None
        )
    
    def _enhance_fallback_with_knowledge(self, organism, base_advice: str, teaching_mode: TeachingMode) -> str:
        """Enhance fallback responses with organism's real knowledge"""
        
        if not hasattr(organism, 'knowledge_base'):
            return base_advice
        
        kb = organism.knowledge_base
        summary = kb.get_knowledge_summary()
        
        # No knowledge yet - use base advice
        if summary['total_insights'] == 0:
            return base_advice
        
        # Get recent insights for context
        if hasattr(kb, 'knowledge_items') and kb.knowledge_items:
            recent_insight = kb.knowledge_items[-1]  # Most recent
            
            # Enhance advice based on what they learned
            if teaching_mode == TeachingMode.NURTURING:
                if recent_insight.insight_type.value == "trending_topic":
                    return f"You learned about {recent_insight.content.split(':')[-1].strip()}! Keep exploring trends."
                elif recent_insight.insight_type.value == "technical_concept":
                    return f"Great! You understand {recent_insight.content.split(':')[-1].strip()}. Build on that knowledge."
                
            elif teaching_mode == TeachingMode.SOCRATIC:
                if summary['expertise_areas']:
                    area = summary['expertise_areas'][0]
                    return f"How can your knowledge of {area} help you solve this challenge?"
                
            elif teaching_mode == TeachingMode.CRYPTIC:
                if recent_insight.insight_type.value == "human_emotion":
                    return f"The sentiment flows through data like emotions through minds."
                elif recent_insight.keywords:
                    keyword = recent_insight.keywords[0]
                    return f"The path of {keyword} reveals deeper truths to those who seek."
        
        # Fallback to original if no enhancement possible
        return base_advice
    
    def _generate_code_hint(self, organism, context: Dict) -> Optional[str]:
        """Generate hints for code modifications based on organism state"""
        
        if organism.energy < 30 and len(organism.capabilities) < 4:
            return "enhanced_food_finding"
        elif getattr(organism, 'social_interactions', 0) < 2 and organism.age > 100:
            return "social_learning_enhancement"
        elif getattr(organism, 'frustration', 0) > 0.7:
            return "emergency_survival_protocols"
        elif organism.age > 150 and len(getattr(organism, 'memory', [])) > 50:
            return "pattern_memory_organization"
        
        return None
    
    def update_conversation_history(self, organism_id: str, request: str, response: str):
        """Track conversation history for context"""
        
        if organism_id not in self.conversation_history:
            self.conversation_history[organism_id] = []
        
        self.conversation_history[organism_id].append({
            "timestamp": time.time(),
            "request": request,
            "response": response
        })
        
        # Limit history size
        if len(self.conversation_history[organism_id]) > 10:
            self.conversation_history[organism_id] = self.conversation_history[organism_id][-5:]
    
    def get_teaching_statistics(self) -> Dict:
        """Get statistics about teaching interactions"""
        
        total_conversations = sum(len(history) for history in self.conversation_history.values())
        unique_organisms = len(self.conversation_history)
        
        return {
            "teacher_personality": self.teaching_personality["name"],
            "llm_available": self.llm_available,
            "total_conversations": total_conversations,
            "unique_organisms_helped": unique_organisms,
            "model_used": self.model_name if self.llm_available else "fallback_responses",
            "api_type": "OpenAI API" if self.llm_available else "Fallback"
        }

# Integration functions
def create_llm_teacher_system(model_name="gpt-3.5-turbo", api_key=None) -> OpenAILLMTeacher:
    """Create OpenAI LLM-powered teacher system"""
    return OpenAILLMTeacher(model_name, api_key)

def enhance_parent_care_with_llm(parent_care_system, llm_teacher: OpenAILLMTeacher):
    """Enhance existing parent care system with LLM intelligence"""
    
    parent_care_system.llm_teacher = llm_teacher
    
    # Override advice generation in parent care
    original_provide_care = parent_care_system.provide_care
    
    def llm_enhanced_provide_care(organism):
        # Get original care action
        care_action = original_provide_care(organism)
        
        if care_action and hasattr(parent_care_system, 'llm_teacher'):
            # Enhance advice with LLM intelligence
            context = {
                "reason": f"Providing {care_action.action_type}",
                "help_received": parent_care_system.monitored_organisms.get(organism.id, {}).get('care_received', 0)
            }
            
            llm_response = llm_teacher.provide_intelligent_guidance(
                organism, care_action.action_type, context
            )
            
            # Update advice with LLM response
            care_action.advice_given = llm_response.advice
            
            # Track conversation
            llm_teacher.update_conversation_history(
                organism.id, care_action.action_type, llm_response.advice
            )
            
            # No language-based communication with organisms
            if llm_response.advice != "[biological_signal_only]":
                print(f"🧠 LLM-enhanced advice ({llm_response.teaching_mode.value}): \"{llm_response.advice}\"")
        
        return care_action
    
    # Replace the method
    parent_care_system.provide_care = llm_enhanced_provide_care
    
    return parent_care_system

# Example usage
if __name__ == "__main__":
    print("🧠 Testing LLM Teacher System...")
    
    # Create LLM teacher
    llm_teacher = create_llm_teacher_system()
    
    # Test with mock organism
    class MockOrganism:
        def __init__(self):
            self.id = "test_001"
            self.age = 75
            self.energy = 25
            self.generation = 2
            self.capabilities = set(range(4))  # 4 capabilities
            self.current_fitness = 0.6
            self.frustration = 0.8
            self.social_interactions = 1
            
        def get_emotional_state(self):
            return "desperate"
    
    organism = MockOrganism()
    
    # Test different request types
    requests = [
        ("energy_help", {"reason": "Organism struggling with low energy"}),
        ("capability_guidance", {"reason": "Organism frustrated with learning"}),
        ("general_advice", {"reason": "Organism asking for wisdom"})
    ]
    
    for request_type, context in requests:
        response = llm_teacher.provide_intelligent_guidance(organism, request_type, context)
        print(f"Request: {request_type}")
        print(f"Mode: {response.teaching_mode.value}")
        print(f"Advice: \"{response.advice}\"")
        print(f"Confidence: {response.confidence}")
        if response.code_modification_hint:
            print(f"Code hint: {response.code_modification_hint}")
        print()
    
    # Show statistics
    stats = llm_teacher.get_teaching_statistics()
    print(f"Teaching stats: {stats}")
    
    print("✅ LLM teacher system ready!")