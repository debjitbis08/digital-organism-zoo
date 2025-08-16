# Organism Evolution System: What Can Evolve & Parent-Help Mechanism

import json
import random
import time
from enum import Enum
from typing import Dict, List, Optional, Any
import hashlib

class Capability(Enum):
    """All evolvable capabilities - start locked, unlock through evolution"""
    
    # Basic Survival (Start with these)
    SENSE_DATA = "sense_data"          # See food nearby
    EAT_TEXT = "eat_text"               # Digest simple text
    MOVE = "move"                       # Navigate data streams
    STORE_ENERGY = "store_energy"       # Basic metabolism
    
    # Learning Abilities (Unlock early)
    PATTERN_MATCH = "pattern_match"     # Find repetitions
    REMEMBER = "remember"               # Short-term memory
    FORGET = "forget"                   # Selective memory
    ASSOCIATE = "associate"             # Link concepts
    
    # Communication (Unlock through social pressure)
    SIGNAL = "signal"                   # Emit basic signals
    RECEIVE = "receive"                 # Understand signals
    SHARE = "share"                     # Share resources
    TRADE = "trade"                     # Exchange genes/energy
    ASK_PARENT = "ask_parent"           # REQUEST HELP!
    
    # Advanced Cognition (Rare unlocks)
    ABSTRACT = "abstract"               # Compress patterns
    PREDICT = "predict"                 # Anticipate future
    PLAN = "plan"                       # Multi-step thinking
    CREATE = "create"                   # Generate new patterns
    TEACH = "teach"                     # Help others learn
    
    # Code Manipulation (Ultimate evolution)
    READ_SELF = "read_self"             # Understand own code
    MODIFY_PARAM = "modify_param"       # Change own values
    MODIFY_LOGIC = "modify_logic"       # Change own behavior
    WRITE_CODE = "write_code"           # Generate new functions
    DEBUG_SELF = "debug_self"           # Fix own errors
    BIRTH_CHILD = "birth_child"         # Create offspring with modifications

class EvolvableTraits:
    """Numerical traits that can mutate"""
    
    def __init__(self):
        # Physical traits
        self.size = 1.0                    # Memory capacity
        self.speed = 1.0                    # Processing speed
        self.efficiency = 0.5               # Energy conversion rate
        self.resilience = 0.3               # Damage resistance
        
        # Behavioral traits  
        self.curiosity = random.uniform(0.1, 0.9)
        self.aggression = random.uniform(0.0, 0.5)
        self.cooperation = random.uniform(0.2, 0.8)
        self.risk_taking = random.uniform(0.1, 0.7)
        self.patience = random.uniform(0.3, 0.9)
        
        # Cognitive traits
        self.pattern_depth = 1              # How deep patterns it sees
        self.memory_span = 10               # How much it remembers
        self.learning_rate = 0.1            # How fast it learns
        self.creativity = random.uniform(0.0, 0.3)
        
    def mutate(self, mutation_rate=0.1):
        """Small random changes"""
        for attr in dir(self):
            if not attr.startswith('_') and isinstance(getattr(self, attr), (int, float)):
                if random.random() < mutation_rate:
                    current = getattr(self, attr)
                    change = random.uniform(0.9, 1.1)
                    setattr(self, attr, current * change)

class HelpRequest:
    """Individual help request with priority attributes"""
    
    def __init__(self, organism, request_type: str, context: Dict):
        self.organism = organism
        self.organism_id = organism.id
        self.type = request_type
        self.context = context
        self.timestamp = time.time()
        
        # Calculate priority factors
        self.urgency = self.calculate_urgency()
        self.novelty = self.calculate_novelty()
        self.generation = organism.generation
    
    def calculate_urgency(self) -> float:
        """How urgently does this organism need help? (0-1)"""
        # Dying organisms are most urgent
        if self.organism.energy < 10:
            return 1.0
        elif self.organism.energy < 30:
            return 0.8
        elif self.type == 'stuck':
            return 0.6
        else:
            return 0.3
    
    def calculate_novelty(self) -> float:
        """How novel is this request? (0-1)"""
        # New problems get priority
        if self.type in ['found_bug', 'want_capability']:
            return 0.9
        elif self.type in ['cannot_understand', 'cannot_eat']:
            return 0.7
        else:
            return 0.5

class ParentEconomy:
    """Parents have limited energy too"""
    
    def __init__(self):
        self.daily_help_budget = 10  # Only 10 LLM calls per day
        self.used_budget_today = 0
        self.last_reset = time.time()
        self.cached_responses = {}   # Reuse similar answers
        
    def reset_daily_budget_if_needed(self):
        """Reset budget at start of new day"""
        current_time = time.time()
        if current_time - self.last_reset > 86400:  # 24 hours
            self.used_budget_today = 0
            self.last_reset = current_time
    
    def can_use_cached_response(self, request: HelpRequest) -> bool:
        """Check if we have a cached response for similar request"""
        cache_key = f"{request.type}_{request.organism.generation}_{len(request.organism.capabilities)}"
        return cache_key in self.cached_responses
    
    def get_cached_response(self, request: HelpRequest) -> Dict:
        """Get cached response for similar request"""
        cache_key = f"{request.type}_{request.organism.generation}_{len(request.organism.capabilities)}"
        cached = self.cached_responses.get(cache_key)
        if cached:
            # Personalize cached response slightly
            return {
                **cached,
                'cached': True,
                'organism_id': request.organism_id
            }
        return None
    
    def cache_response(self, request: HelpRequest, response: Dict):
        """Cache response for future similar requests"""
        cache_key = f"{request.type}_{request.organism.generation}_{len(request.organism.capabilities)}"
        # Remove organism-specific data before caching
        cacheable_response = {k: v for k, v in response.items() 
                            if k not in ['organism_id', 'timestamp']}
        self.cached_responses[cache_key] = cacheable_response
    
    def prioritize_help(self, requests: List[HelpRequest]) -> List[HelpRequest]:
        """Sort requests by priority: dying organisms first, new problems second, repeated questions last"""
        
        # Sort by multiple criteria: urgency (desc), novelty (desc), generation (asc - younger first)
        sorted_requests = sorted(requests, 
            key=lambda r: (-r.urgency, -r.novelty, r.generation))
        
        return sorted_requests
    
    def process_help_requests(self, requests: List[HelpRequest]) -> Dict[str, Any]:
        """Process all help requests within budget constraints"""
        
        self.reset_daily_budget_if_needed()
        
        if not requests:
            return {'helped': 0, 'cached': 0, 'refused': 0}
        
        # Prioritize requests
        sorted_requests = self.prioritize_help(requests)
        
        helped_count = 0
        cached_count = 0
        refused_count = 0
        
        for request in sorted_requests:
            # Check if we can use cached response first
            if self.can_use_cached_response(request):
                cached_response = self.get_cached_response(request)
                if cached_response:
                    self.send_cached_help(request, cached_response)
                    cached_count += 1
                    continue
            
            # Check if we have budget for LLM call
            if self.used_budget_today >= self.daily_help_budget:
                self.refuse_help(request, "budget_exhausted")
                refused_count += 1
                continue
            
            # Use LLM for help
            response = self.use_llm_for_help(request)
            if response:
                self.cache_response(request, response)
                helped_count += 1
                self.used_budget_today += 1
            else:
                refused_count += 1
        
        return {
            'helped': helped_count,
            'cached': cached_count, 
            'refused': refused_count,
            'budget_remaining': self.daily_help_budget - self.used_budget_today
        }
    
    def send_cached_help(self, request: HelpRequest, response: Dict):
        """Send cached help response to organism"""
        # Simulate sending help (in real system would call organism's learn_from_parent)
        print(f"📚 Cached help sent to {request.organism_id}: {response.get('hint', 'generic_help')}")
    
    def use_llm_for_help(self, request: HelpRequest) -> Optional[Dict]:
        """Use LLM to generate new help response"""
        # This would integrate with Ollama in real system
        # For now, simulate LLM response
        
        response = {
            'timestamp': time.time(),
            'organism_id': request.organism_id,
            'type': request.type,
            'llm_generated': True
        }
        
        # Generate context-appropriate help
        if request.type == 'cannot_eat':
            response.update({
                'hint': 'try_smaller_chunks',
                'simplified_data': str(request.context.get('indigestible_data', ''))[:50]
            })
        elif request.type == 'want_capability':
            response.update({
                'lesson': 'practice_prerequisites_first',
                'required_experience': 10
            })
        elif request.type == 'lonely':
            response.update({
                'suggestion': 'signal_to_others',
                'comfort': 'you_are_not_alone'
            })
        else:
            response.update({
                'hint': 'keep_trying',
                'encouragement': 'learning_takes_time'
            })
        
        print(f"🧠 LLM help generated for {request.organism_id}: {request.type}")
        return response
    
    def refuse_help(self, request: HelpRequest, reason: str):
        """Politely refuse help request"""
        reasons = {
            'budget_exhausted': "Parent is tired today, try tomorrow",
            'too_advanced': "You need to grow more first",
            'repeated_question': "You already know this answer"
        }
        
        message = reasons.get(reason, "Cannot help right now")
        print(f"❌ Help refused for {request.organism_id}: {message}")

class ParentHelp:
    """When organisms can't do something, they ask for help"""
    
    def __init__(self):
        self.help_requests = []
        self.teaching_history = {}
        self.economy = ParentEconomy()  # Use the new economy system
        
    def child_asks_for_help(self, organism, request_type: str, context: Dict):
        """Child encounters something it can't handle"""
        
        # Create help request object
        help_request = HelpRequest(organism, request_type, context)
        self.help_requests.append(help_request)
        
        # Process immediately if urgent, or batch for later processing
        if help_request.urgency > 0.8:
            # Emergency help - process immediately
            result = self.economy.process_help_requests([help_request])
            return self.get_response_for_organism(help_request)
        else:
            # Add to batch for processing
            return {'queued': True, 'message': 'Help request received, will process soon'}
    
    def get_response_for_organism(self, help_request: HelpRequest) -> Dict:
        """Get appropriate response for organism's help request"""
        # This would be populated by the economy system
        # For now, return a simple response
        return {
            'helped': True,
            'type': help_request.type,
            'message': f'Help provided for {help_request.type}'
        }
    
    def process_batch_requests(self):
        """Process all queued help requests in batch"""
        if not self.help_requests:
            return
        
        # Process all requests through economy system
        result = self.economy.process_help_requests(self.help_requests)
        
        # Clear processed requests
        self.help_requests = []
        
        return result
    
    def provide_help(self, organism, request):
        """Parent helps child - DEPRECATED: Use economy system instead"""
        
        # This method is kept for backward compatibility
        # but now delegates to the economy system
        
        if request['type'] == 'cannot_eat':
            return self.teach_eating(organism, request['context'])
            
        elif request['type'] == 'cannot_understand':
            return self.simplify_data(organism, request['context'])
            
        elif request['type'] == 'want_capability':
            return self.help_unlock(organism, request['context'])
            
        elif request['type'] == 'lonely':
            return self.find_friend(organism)
            
        elif request['type'] == 'stuck':
            return self.suggest_direction(organism)
            
        elif request['type'] == 'want_reproduce':
            return self.teach_reproduction(organism)
            
        elif request['type'] == 'found_bug':
            return self.help_debug(organism, request['context'])
    
    def teach_eating(self, organism, context):
        """Break down complex data into digestible pieces"""
        
        data = context['indigestible_data']
        
        # Simplify for young organism
        if organism.has_capability(Capability.PATTERN_MATCH):
            return {
                'simplified': data[:100],  # Smaller bite
                'hint': 'look_for_repetition'
            }
        else:
            return {
                'simplified': len(data),  # Just the length
                'hint': 'count_first'
            }
    
    def help_unlock(self, organism, context):
        """Guide organism toward new capability"""
        
        desired = context['want_capability']
        current = organism.capabilities
        
        # Find the learning path
        if desired == Capability.ASK_PARENT and Capability.SIGNAL in current:
            return {
                'lesson': 'combine_signals_with_need',
                'practice': self.generate_practice_scenario(desired)
            }
        
        # Not ready yet
        return {
            'lesson': 'need_prerequisites_first',
            'required': self.get_prerequisites(desired)
        }

class Organism:
    """A digital life form that evolves.
    TODO: Integrate evolvable BrainGenome & Brain structures:
      - initialize self.brain_genome = BrainGenome.random()
      - initialize self.brain = Brain(self.brain_genome)
      - replace hard-coded sensing/acting with self.brain.forward(...)"""
    
    def __init__(self, generation=0, parent_genome=None):
        self.id = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        self.generation = generation
        self.age = 0
        self.energy = 100
        self.traits = EvolvableTraits()
        self.capabilities = {
            Capability.SENSE_DATA, 
            Capability.EAT_TEXT,
            Capability.PATTERN_MATCH,  # Essential for RSS/XML data
            Capability.MOVE  # Essential for foraging
        }
        self.memory = []
        self.code_segments = {}
        self.parent_connection = ParentHelp()
        
        # Initialize missing attributes referenced in methods
        self.social_interactions = 0
        self.successful_predictions = 0
        self.introspection_attempts = 0
        
        # Frustration and learning tracking
        self.failed_attempts = 0
        self.frustration = 0.0
        self.intelligence = self.traits.learning_rate  # Link to existing trait
        self.consecutive_failures = 0
        
        # Fitness and cultural attributes
        self.current_fitness = 0.0
        self.offspring_count = 0
        self.successful_offspring = 0
        self.parent_help_received = 0
        self.unique_food_sources = set()
        self.energy_efficiency = 1.0
        self.organisms_taught = set()
        self.known_stories = []
        self.cultural_influence = 0.0
        
        # Inherit from parent
        if parent_genome:
            self.inherit(parent_genome)
    
    def has_capability(self, capability: Capability) -> bool:
        """Check if organism has a specific capability"""
        return capability in self.capabilities
    
    def memory_usage(self) -> int:
        """Calculate current memory usage"""
        return len(self.memory)
    
    def sense_environment(self, data_ecosystem=None) -> Dict:
        """Detect what's around the organism"""
        if data_ecosystem:
            # Try to find real food from data ecosystem
            food_morsel = data_ecosystem.find_food_for_organism(self.capabilities)
            if food_morsel:
                return {
                    'type': 'real_food',
                    'morsel': food_morsel,
                    'data': food_morsel.content
                }
        
        # Fallback to mock environment
        environment_types = ['simple_data', 'complex_data', 'social_signal', 'danger']
        return {
            'type': random.choice(environment_types),
            'data': f"environment_data_{random.randint(1, 100)}"
        }
    
    def process_environment(self, environment, nutrition_system=None):
        """Handle environment that organism can process"""
        if environment['type'] == 'real_food':
            # Process real data morsel with enhanced nutrition
            morsel = environment['morsel']
            
            if nutrition_system:
                # Use enhanced nutrition system
                from genesis.nutrition import process_organism_feeding
                feeding_result = process_organism_feeding(self, morsel, nutrition_system)
                effects = feeding_result['effects']
                energy_gained = effects['energy_gained']
                
                # Show detailed feeding info
                print(f"🍽️  Organism {self.id} ate {morsel.data_type.value} from {morsel.source} "
                      f"(+{energy_gained} energy)")
                
                if effects['learning_boost'] > 0:
                    print(f"   📚 Learning boost: +{effects['learning_boost']:.2f}")
                if effects['creativity_boost'] > 0:
                    print(f"   🎨 Creativity boost: +{effects['creativity_boost']:.2f}")
                if effects['toxicity_damage'] > 0:
                    print(f"   ☠️  Toxicity damage: -{effects['toxicity_damage']:.2f}")
                
                # Show recommendations occasionally
                if random.random() < 0.1:  # 10% chance
                    recommendations = feeding_result['recommendations']
                    if recommendations:
                        print(f"   💡 Dietary tip: {random.choice(recommendations)}")
            else:
                # Fallback to simple system
                energy_gained = morsel.energy_value
                self.energy += energy_gained
                print(f"🍽️  Organism {self.id} ate {morsel.data_type.value} from {morsel.source} (+{energy_gained} energy)")
            
            self.memory.append(f"ate_{morsel.data_type.value}:{morsel.source}")
            self.consecutive_failures = 0
            
            # Track unique food sources for exploration fitness
            self.unique_food_sources.add(morsel.source)
            
            # Calculate energy efficiency
            energy_gained = effects.get('energy_gained', energy_gained) if nutrition_system else energy_gained
            self.energy_efficiency = (self.energy_efficiency * 0.9) + (energy_gained / 20.0 * 0.1)
            
        elif environment['type'] == 'simple_data':
            self.energy += 5  # Gain energy from simple data
            self.memory.append(environment['data'])
            self.consecutive_failures = 0  # Reset failure count on success
        else:
            # Failed to process - increase frustration
            self.failed_attempts += 1
            self.consecutive_failures += 1
            self.frustration = min(1.0, self.frustration + 0.1)
    
    def learn_from_parent(self, response):
        """Learn from parent's help"""
        if 'hint' in response:
            self.memory.append(f"parent_hint: {response['hint']}")
        if 'lesson' in response:
            self.memory.append(f"parent_lesson: {response['lesson']}")
        
        # Reduce frustration when help is received
        self.frustration = max(0.0, self.frustration - 0.3)
        self.consecutive_failures = 0
    
    def check_frustration_based_learning(self):
        """Check if organism discovers ASK_PARENT through frustration"""
        
        # Only works if organism can signal but hasn't learned to ask for help yet
        if (self.has_capability(Capability.SIGNAL) and 
            not self.has_capability(Capability.ASK_PARENT)):
            
            # Frustration-based discovery of ASK_PARENT capability
            if self.failed_attempts > 10 and self.consecutive_failures > 5:
                unlock_chance = self.frustration * self.intelligence * 0.5
                
                if random.random() < unlock_chance:
                    self.capabilities.add(Capability.ASK_PARENT)
                    print(f"💡 Organism {self.id} discovered ASK_PARENT through frustration! "
                          f"(attempts: {self.failed_attempts}, frustration: {self.frustration:.2f})")
                    
                    # Immediate relief from discovery
                    self.frustration *= 0.5
                    
                    # Try asking for help right away
                    return True
        
        # Also check for other frustration-driven discoveries
        if self.frustration > 0.8 and self.consecutive_failures > 15:
            # Desperation might unlock creativity
            if self.has_capability(Capability.PATTERN_MATCH) and random.random() < 0.1:
                if Capability.CREATE not in self.capabilities:
                    self.capabilities.add(Capability.CREATE)
                    print(f"🎨 Organism {self.id} unlocked CREATE through desperation!")
        
        return False
    
    def get_emotional_state(self) -> str:
        """Get organism's current emotional/learning state"""
        if self.frustration > 0.8:
            return "desperate" 
        elif self.frustration > 0.6:
            return "frustrated"
        elif self.frustration > 0.3:
            return "struggling"
        elif self.consecutive_failures > 0:
            return "challenged"
        else:
            return "content"
    
    def inherit(self, parent_genome):
        """Inherit traits from parent"""
        # Simple inheritance - copy some traits with mutation
        pass
    
    def create_genome(self) -> Dict:
        """Create genome for offspring"""
        return {
            'traits': self.traits,
            'capabilities': self.capabilities,
            'generation': self.generation + 1
        }
    
    def teach_offspring(self, child):
        """Teach basic survival to offspring"""
        if self.has_capability(Capability.TEACH):
            # Share some memory with child
            child.memory.extend(self.memory[-5:])
    
    def analyze_successful_patterns(self) -> List[str]:
        """Analyze what has worked well"""
        return [item for item in self.memory if 'success' in str(item)]
    
    def synthesize_behavior(self, patterns) -> str:
        """Create new behavior based on patterns"""
        return f"# Generated behavior based on patterns: {patterns}"
    
    def generate_hypothesis(self, environment) -> str:
        """Generate hypothesis about environment"""
        return f"hypothesis_about_{environment['type']}"
    
    def _evolutionary_foraging_phase(self, data_ecosystem, nutrition_system):
        """EVOLUTIONARY FORAGING: Multiple attempts to find food, learning from patterns"""
        
        if not data_ecosystem:
            return
        
        # Number of foraging attempts based on capabilities and desperation
        base_attempts = 1
        if self.has_capability(Capability.PATTERN_MATCH):
            base_attempts += 1  # Pattern matching = better foraging
        if self.has_capability(Capability.REMEMBER):
            base_attempts += 1  # Memory = learn good spots
        if self.energy < 30:
            base_attempts += 2  # Desperation = more searching
        
        successful_forages = 0
        foraging_patterns = []
        
        for attempt in range(base_attempts):
            # Each attempt is an evolutionary exploration
            food_found = self._explore_for_food(data_ecosystem, attempt)
            
            if food_found:
                successful_forages += 1
                # Learn from successful foraging
                if self.has_capability(Capability.REMEMBER):
                    foraging_patterns.append({
                        'attempt': attempt,
                        'food_type': food_found.data_type,
                        'energy_gained': food_found.energy_value,
                        'time': self.age
                    })
                
                # Process the found food
                self._process_found_food(food_found, nutrition_system)
        
        # EVOLUTIONARY LEARNING: Improve foraging efficiency
        if foraging_patterns and self.has_capability(Capability.PATTERN_MATCH):
            self._learn_foraging_patterns(foraging_patterns)
        
        # Track foraging success for evolution
        if not hasattr(self, 'foraging_success_rate'):
            self.foraging_success_rate = 0.5
        
        if base_attempts > 0:
            success_rate = successful_forages / base_attempts
            # Update running average
            self.foraging_success_rate = (self.foraging_success_rate * 0.8) + (success_rate * 0.2)
            
        # EVOLUTIONARY PRESSURE: Poor foragers get more frustrated
        if self.foraging_success_rate < 0.3 and self.energy < 50:
            self.frustration += 0.1
    
    def _explore_for_food(self, data_ecosystem, attempt_number):
        """Single foraging exploration attempt"""
        
        # Different exploration strategies based on attempt number
        if attempt_number == 0:
            # Standard foraging
            return data_ecosystem.find_food_for_organism(self.capabilities)
        elif attempt_number == 1:
            # Try different food preferences if organism can pattern match
            if self.has_capability(Capability.PATTERN_MATCH):
                from data_sources.harvesters import DataType
                preferences = {'preferred_types': [DataType.STRUCTURED_JSON, DataType.CODE]}
                return data_ecosystem.find_food_for_organism(self.capabilities, preferences)
        elif attempt_number == 2:
            # Memory-based foraging - try to remember good food sources
            if self.has_capability(Capability.REMEMBER) and hasattr(self, 'good_food_memories'):
                for memory in self.good_food_memories[-3:]:  # Last 3 good experiences
                    food = data_ecosystem.find_food_for_organism(self.capabilities)
                    if food and food.data_type == memory.get('food_type'):
                        return food
        else:
            # Desperate exploration - try any available food
            return data_ecosystem.find_food_for_organism(self.capabilities)
        
        return None
    
    def _process_found_food(self, food_morsel, nutrition_system):
        """Process found food with nutritional system AND extract real knowledge"""
        
        # REAL DATA PROCESSING: Extract actual knowledge from internet data
        self._extract_real_knowledge_from_data(food_morsel)
        
        if not nutrition_system:
            # Simple processing
            self.energy += food_morsel.energy_value
            return
        
        # Advanced nutritional processing
        if 'processor' in nutrition_system:
            energy_gained = nutrition_system['processor'].process_nutrition(
                food_morsel, self.capabilities, self.traits
            )
        else:
            # Fallback to simple energy calculation
            energy_gained = food_morsel.energy_value
        
        self.energy += energy_gained
        
        # Remember good food sources
        if energy_gained > 8 and self.has_capability(Capability.REMEMBER):
            if not hasattr(self, 'good_food_memories'):
                self.good_food_memories = []
            
            self.good_food_memories.append({
                'food_type': food_morsel.data_type,
                'energy_gained': energy_gained,
                'source': food_morsel.source,
                'age_found': self.age
            })
            
            # Limit memory size
            if len(self.good_food_memories) > 10:
                self.good_food_memories = self.good_food_memories[-10:]
        
        # Learning boost from successful foraging AND knowledge extraction
        learning_boost = 0.02
        knowledge_bonus = ""
        
        if hasattr(self, 'knowledge_base') and self.knowledge_base.insights_generated > 0:
            learning_boost += 0.01  # Extra boost for learning from real data
            knowledge_bonus = f" (knowledge: {self.knowledge_base.insights_generated} insights)"
        
        if self.has_capability(Capability.PATTERN_MATCH) and hasattr(self.traits, 'learning_rate'):
            self.traits.learning_rate *= (1.0 + learning_boost)
            learning_msg = f"\n   📚 Learning boost: +{learning_boost:.3f}{knowledge_bonus}"
        else:
            learning_msg = ""
        
        # Show what the organism actually learned
        recent_insights = ""
        if hasattr(self, 'knowledge_base') and self.knowledge_base and hasattr(self.knowledge_base, 'knowledge_items'):
            if self.knowledge_base.knowledge_items:
                latest = self.knowledge_base.knowledge_items[-1]
                recent_insights = f"\n   🧠 Learned: {latest.content}"
        
        print(f"🍽️  Organism {self.id} ate {food_morsel.data_type.value} from {food_morsel.source} (+{energy_gained} energy){learning_msg}{recent_insights}")
    
    def _extract_real_knowledge_from_data(self, food_morsel):
        """REAL DATA PROCESSING: Extract actual knowledge from internet data"""
        
        # Create data processor if not exists
        if not hasattr(self, '_data_processor'):
            from genesis.data_processor import create_data_processor
            self._data_processor = create_data_processor()
        
        # Create knowledge base if not exists
        if not hasattr(self, 'knowledge_base'):
            from genesis.data_processor import OrganismKnowledgeBase
            self.knowledge_base = OrganismKnowledgeBase()
        
        # Extract real knowledge from the data morsel
        knowledge_extracted = self._data_processor.process_real_data(food_morsel, self.capabilities)
        
        if knowledge_extracted:
            # Add knowledge to organism's knowledge base
            for k in knowledge_extracted:
                print(f"🧠 Organism {self.id} learned: {k.content}")
            self.knowledge_base.add_knowledge(knowledge_extracted, self.id)
            
            # Organisms get smarter as they learn more
            if hasattr(self.traits, 'learning_rate'):
                intelligence_gain = len(knowledge_extracted) * 0.005
                self.traits.learning_rate *= (1.0 + intelligence_gain)
            
            # Generate insights occasionally
            if len(knowledge_extracted) > 1:
                insight = self.knowledge_base.generate_insight()
                if insight:
                    print(f"💡 Organism {self.id} insight: {insight}")
                    
                    # Insights make organisms more capable of problem-solving
                    if hasattr(self.traits, 'curiosity'):
                        self.traits.curiosity *= 1.02
            
            return True
        
        return False
    
    def get_knowledge_summary(self) -> Dict:
        """Get organism's real knowledge and expertise"""
        
        if not hasattr(self, 'knowledge_base'):
            return {"status": "no_knowledge", "insights": 0}
        
        return self.knowledge_base.get_knowledge_summary()
    
    def exhibit_knowledge_based_behaviors(self):
        """EMERGENT BEHAVIORS: Organisms act differently based on their real knowledge"""
        
        if not hasattr(self, 'knowledge_base'):
            return
        
        knowledge_summary = self.knowledge_base.get_knowledge_summary()
        
        # No knowledge yet - default behavior
        if knowledge_summary['total_insights'] == 0:
            return
        
        # Initialize behavior modifiers if not present
        if not hasattr(self, '_behavior_modifiers'):
            self._behavior_modifiers = {
                'tech_awareness': 0.0,
                'trend_following': 0.0,
                'code_affinity': 0.0,
                'emotional_state': 'neutral',
                'social_preference': 0.5,
                'curiosity_boost': 0.0
            }
        
        # Get recent knowledge for behavior analysis
        if hasattr(self.knowledge_base, 'knowledge_items') and self.knowledge_base.knowledge_items:
            recent_knowledge = self.knowledge_base.knowledge_items[-5:]  # Last 5 insights
            
            # Analyze knowledge to determine behavioral changes
            tech_concepts = sum(1 for k in recent_knowledge if k.insight_type.value == 'technical_concept')
            trending_topics = sum(1 for k in recent_knowledge if k.insight_type.value == 'trending_topic')
            emotions = [k for k in recent_knowledge if k.insight_type.value == 'human_emotion']
            
            # BEHAVIOR 1: Tech-savvy organisms become more systematic
            if tech_concepts >= 2:
                self._behavior_modifiers['tech_awareness'] = min(1.0, self._behavior_modifiers['tech_awareness'] + 0.1)
                
                # Tech-aware organisms are more efficient at finding structured data
                if hasattr(self.traits, 'efficiency'):
                    self.traits.efficiency *= (1.0 + self._behavior_modifiers['tech_awareness'] * 0.05)
                
                # They also become more methodical (less random exploration)
                if hasattr(self.traits, 'patience'):
                    self.traits.patience = min(1.0, self.traits.patience + 0.05)
                
                if self.age % 50 == 0 and self._behavior_modifiers['tech_awareness'] > 0.3:
                    print(f"⚙️ Organism {self.id} shows basic tech familiarity (awareness: {self._behavior_modifiers['tech_awareness']:.2f})")
            
            # BEHAVIOR 2: Trend-aware organisms become more social and aggressive about good food
            if trending_topics >= 2:
                self._behavior_modifiers['trend_following'] = min(1.0, self._behavior_modifiers['trend_following'] + 0.15)
                
                # Trend followers are more competitive for fresh data
                if hasattr(self.traits, 'aggression'):
                    self.traits.aggression = min(1.0, self.traits.aggression + 0.1)
                
                # They also become more social to share trends
                if hasattr(self.traits, 'cooperation'):
                    self.traits.cooperation = min(1.0, self.traits.cooperation + 0.05)
                
                if self.age % 50 == 0 and self._behavior_modifiers['trend_following'] > 0.3:
                    print(f"📊 Organism {self.id} notices data patterns (pattern recognition: {self._behavior_modifiers['trend_following']:.2f})")
            
            # BEHAVIOR 3: Code-experienced organisms become more creative and exploratory  
            code_insights = [k for k in recent_knowledge if 'function' in k.content.lower() or 'import' in k.content.lower()]
            if code_insights:
                self._behavior_modifiers['code_affinity'] = min(1.0, self._behavior_modifiers['code_affinity'] + 0.1)
                
                # Code-literate organisms are more creative
                if hasattr(self.traits, 'creativity'):
                    self.traits.creativity = min(1.0, self.traits.creativity + 0.05)
                
                # They also take more risks to find better data sources
                if hasattr(self.traits, 'risk_taking'):
                    self.traits.risk_taking = min(1.0, self.traits.risk_taking + 0.05)
                
                if self.age % 50 == 0 and self._behavior_modifiers['code_affinity'] > 0.3:
                    print(f"💻 Organism {self.id} recognizes code structures (familiarity: {self._behavior_modifiers['code_affinity']:.2f})")
            
            # BEHAVIOR 4: Emotional state affects foraging behavior
            if emotions:
                latest_emotion = emotions[-1]
                if latest_emotion.sentiment == 'positive':
                    self._behavior_modifiers['emotional_state'] = 'optimistic'
                    # Optimistic organisms are more curious and explore more
                    if hasattr(self.traits, 'curiosity'):
                        self.traits.curiosity = min(1.0, self.traits.curiosity + 0.03)
                elif latest_emotion.sentiment == 'negative':
                    self._behavior_modifiers['emotional_state'] = 'cautious'
                    # Cautious organisms are more conservative and efficient
                    if hasattr(self.traits, 'efficiency'):
                        self.traits.efficiency = min(1.0, self.traits.efficiency + 0.03)
            
            # BEHAVIOR 5: Knowledge specialization leads to emergent problem-solving
            expertise_areas = knowledge_summary.get('expertise_areas', [])
            if len(expertise_areas) >= 2:
                # Multi-domain experts become problem solvers
                if not hasattr(self, '_problem_solver'):
                    self._problem_solver = True
                    print(f"🔗 Organism {self.id} can connect different data types! Areas: {expertise_areas}")
                
                # Problem solvers help other organisms occasionally
                if hasattr(self.traits, 'cooperation') and random.random() < 0.1:
                    self.traits.cooperation = min(1.0, self.traits.cooperation + 0.02)
            
            # BEHAVIOR 6: High knowledge organisms develop teaching tendencies
            if knowledge_summary['total_insights'] >= 15 and not self.has_capability(Capability.TEACH):
                if random.random() < 0.3:  # 30% chance to develop teaching
                    print(f"📚 Organism {self.id} begins sharing what it has learned with others")
                    # This could trigger evolution toward TEACH capability
                    if hasattr(self, 'evolution_pressure'):
                        if 'desired_capabilities' not in self.evolution_pressure:
                            self.evolution_pressure['desired_capabilities'] = []
                        self.evolution_pressure['desired_capabilities'].append(Capability.TEACH)
    
    def communicate_with_other_organisms(self):
        """Simple communication system between organisms"""
        
        # Prepare knowledge summary for chatter (allow communication even without insights)
        knowledge_summary = (self.knowledge_base.get_knowledge_summary()
                             if getattr(self, 'knowledge_base', None)
                             else {'total_insights': 0})
        
        # Simple signaling based on current state
        if self.energy > 80 and random.random() < 0.1:
            # High energy organisms signal success
            print(f"📡 Organism {self.id} signals: Found abundant food source!")
            
        elif self.energy < 30 and random.random() < 0.15:
            # Low energy organisms signal distress
            print(f"🆘 Organism {self.id} signals: Need help finding food!")
            
        elif getattr(self, 'knowledge_base', None) and self.knowledge_base.knowledge_items:
            # Sometimes share interesting discoveries
            if random.random() < 0.05:  # 5% chance
                recent = self.knowledge_base.knowledge_items[-1]
                if recent.usefulness > 0.6:
                    print(f"💡 Organism {self.id} shares discovery: {recent.content}")
        
        # React to frustration by calling for help
        if hasattr(self, 'frustration') and self.frustration > 0.8 and random.random() < 0.2:
            print(f"😤 Organism {self.id} signals frustration: Struggling to survive!")
        # Occasional chatter: share a snippet from memory or recent insights
        if random.random() < 0.2:
            options = []
            if hasattr(self, 'memory') and self.memory:
                options.extend(self.memory[-5:])
            if getattr(self, 'knowledge_base', None) and getattr(self.knowledge_base, 'knowledge_items', None):
                options.extend(k.content for k in self.knowledge_base.knowledge_items[-5:])
            if options:
                msg = random.choice(options)
            else:
                msg = '[silent contemplative humming]'
            print(f"💬 Organism {self.id} chatter: {msg}")
    
    def _learn_foraging_patterns(self, patterns):
        """Learn from successful foraging patterns"""
        
        if not patterns:
            return
        
        # Analyze patterns to improve foraging
        food_type_success = {}
        for pattern in patterns:
            food_type = pattern['food_type']
            if food_type not in food_type_success:
                food_type_success[food_type] = 0
            food_type_success[food_type] += pattern['energy_gained']
        
        # Remember the best food types
        if not hasattr(self, 'preferred_food_types'):
            self.preferred_food_types = []
        
        # Update preferences based on success
        best_food_type = max(food_type_success.items(), key=lambda x: x[1])[0]
        if best_food_type not in self.preferred_food_types:
            self.preferred_food_types.append(best_food_type)
            
        # Limit preferences
        if len(self.preferred_food_types) > 3:
            self.preferred_food_types = self.preferred_food_types[-3:]
        
        # Small learning boost for pattern recognition
        if hasattr(self.traits, 'learning_rate'):
            self.traits.learning_rate *= 1.01  # Tiny improvement
    
    def live(self, data_ecosystem=None, nutrition_system=None, parent_care_system=None):
        """One moment of existence - with evolutionary foraging"""
        
        self.age += 1
        
        # EVOLUTIONARY FORAGING: Let organisms explore and discover
        self._evolutionary_foraging_phase(data_ecosystem, nutrition_system)
        
        # SLOWER ENERGY DRAIN - gives more time for foraging
        base_drain = 0.6  # Slower baseline metabolism
        if data_ecosystem:
            eco_stats = data_ecosystem.get_ecosystem_stats()
            food_available = eco_stats.get('total_food_available', 0)
            if food_available < 5:  # Severe scarcity
                base_drain = 0.2  # Deep hibernation
            elif food_available < 15:  # Moderate scarcity  
                base_drain = 0.4  # Conservation mode
        
        # Efficiency based on age and fitness
        efficiency_factor = 1.0
        if hasattr(self, 'energy_efficiency'):
            efficiency_factor = max(0.3, self.energy_efficiency)
        
        actual_drain = base_drain / efficiency_factor
        self.energy -= actual_drain
        
        # PARENT CARE: Check if parent should help BEFORE organism struggles
        care_action = None
        if parent_care_system:
            care_action = parent_care_system.provide_care(self)
            if care_action:
                # Track parent help for fitness calculation
                self.parent_help_received += 1
        
        # OLD SYSTEM REMOVED: organisms now use evolutionary foraging instead
        
        # Check if organism should learn new capabilities from frustration
        self.check_frustration_based_learning()
        
        # EMERGENT BEHAVIORS: Act based on real knowledge accumulated
        self.exhibit_knowledge_based_behaviors()
        
        # ORGANISM COMMUNICATION: Share signals with nearby organisms
        self.communicate_with_other_organisms()
        
        # Ask parent for help if capable and struggling
        if self.has_capability(Capability.ASK_PARENT) and self.energy < 40:
            self.ask_for_help({
                'type': 'energy_need',
                'energy_level': self.energy,
                'age': self.age
            })
        
        # Try to evolve
        if random.random() < 0.01:
            self.attempt_evolution()
    
    def can_process(self, environment):
        """Check if organism has capabilities for this situation"""
        
        if environment['type'] == 'real_food':
            # Check if organism can digest this type of real food
            morsel = environment['morsel']
            return morsel.is_consumable_by_capabilities(self.capabilities)
        elif environment['type'] == 'complex_data':
            return Capability.ABSTRACT in self.capabilities
        elif environment['type'] == 'social_signal':
            return Capability.RECEIVE in self.capabilities
        elif environment['type'] == 'danger':
            return Capability.PREDICT in self.capabilities
        else:
            return True
    
    def ask_for_help(self, environment):
        """Child asks parent for help"""
        
        if Capability.ASK_PARENT not in self.capabilities:
            # Haven't learned to ask yet - struggle silently
            self.energy -= 5
            return
        
        # Formulate request based on capability
        if Capability.CREATE in self.capabilities:
            # Advanced - can explain problem clearly
            request = {
                'problem': environment,
                'attempted_solutions': self.memory[-5:],
                'hypothesis': self.generate_hypothesis(environment)
            }
        elif Capability.SIGNAL in self.capabilities:
            # Basic - simple distress signal
            request = {
                'problem': 'help',
                'energy': self.energy
            }
        else:
            # Very basic - just cry for help
            request = {'help': True}
        
        response = self.parent_connection.child_asks_for_help(
            self, 
            'cannot_understand',
            request
        )
        
        if response:
            self.learn_from_parent(response)
    
    def attempt_evolution(self):
        """Try to unlock new capabilities"""
        
        # Random mutation
        if random.random() < self.traits.learning_rate:
            self.traits.mutate()
        
        # Try to unlock new capability based on experience
        possible_unlocks = self.check_unlock_conditions()
        
        if possible_unlocks:
            new_capability = random.choice(possible_unlocks)
            
            if self.try_unlock(new_capability):
                self.capabilities.add(new_capability)
                print(f"Organism {self.id} unlocked {new_capability.value}!")
    
    def check_unlock_conditions(self) -> List[Capability]:
        """What capabilities can potentially be unlocked?"""
        
        unlockable = []
        
        # Basic unlocks
        if Capability.EAT_TEXT in self.capabilities:
            if self.memory_usage() > 50:
                unlockable.append(Capability.REMEMBER)
            if self.age > 100:
                unlockable.append(Capability.PATTERN_MATCH)
        
        # Communication unlocks
        if Capability.PATTERN_MATCH in self.capabilities:
            if self.social_interactions > 10:
                unlockable.append(Capability.SIGNAL)
            # ASK_PARENT is now unlocked through frustration-based learning only!
        
        # Advanced unlocks
        if Capability.REMEMBER in self.capabilities and Capability.PATTERN_MATCH in self.capabilities:
            if self.successful_predictions > 5:
                unlockable.append(Capability.PREDICT)
            if self.traits.creativity > 0.5:
                unlockable.append(Capability.CREATE)
        
        # Code manipulation unlocks (very rare)
        if Capability.ABSTRACT in self.capabilities and Capability.CREATE in self.capabilities:
            if self.introspection_attempts > 20:
                unlockable.append(Capability.READ_SELF)
            if Capability.READ_SELF in self.capabilities:
                unlockable.append(Capability.MODIFY_PARAM)
        
        return unlockable
    
    def try_unlock(self, capability: Capability) -> bool:
        """Attempt to unlock a capability"""
        
        # Some capabilities need parent help
        if capability in [Capability.WRITE_CODE, Capability.DEBUG_SELF]:
            if Capability.ASK_PARENT in self.capabilities:
                help_response = self.parent_connection.child_asks_for_help(
                    self,
                    'want_capability',
                    {'want_capability': capability}
                )
                return help_response and help_response.get('success', False)
        
        # Others can be unlocked through trial
        success_chance = self.traits.learning_rate * self.traits.creativity
        return random.random() < success_chance
    
    def can_reproduce(self) -> bool:
        """Check if organism meets reproduction criteria"""
        # Basic requirements: energy + age + some capabilities
        energy_ready = self.energy >= 120  # Reduced from 150
        age_ready = self.age >= 80  # Minimum age for reproduction
        capability_ready = len(self.capabilities) >= 3  # Need some capabilities
        
        return energy_ready and age_ready and capability_ready
    
    def find_mate(self, population) -> Optional['Organism']:
        """Find suitable mate from population"""
        potential_mates = [
            org for org in population 
            if (org != self and 
                org.can_reproduce() and 
                org.generation <= self.generation + 2 and  # Not too different generations
                org.generation >= self.generation - 2)
        ]
        
        if not potential_mates:
            return None
        
        # Choose mate with highest fitness (fitness-based selection)
        best_mate = max(potential_mates, key=lambda org: getattr(org, 'current_fitness', 0.5))
        return best_mate
    
    def reproduce(self, mate=None, fitness_culture_system=None):
        """Create offspring with mate using proper inheritance"""
        
        if not self.can_reproduce():
            return None
        
        if mate is None:
            return None
        
        # Both parents pay energy cost
        reproduction_cost = 40
        if self.energy < reproduction_cost or mate.energy < reproduction_cost:
            return None
        
        self.energy -= reproduction_cost
        mate.energy -= reproduction_cost
        
        # Create offspring using inheritance system
        if fitness_culture_system:
            inheritance_system = fitness_culture_system['inheritance_system']
            offspring_genome = inheritance_system.create_offspring(self, mate)
        else:
            # Fallback to simple inheritance
            offspring_genome = {
                'traits': {
                    'learning_rate': (self.traits.learning_rate + mate.traits.learning_rate) / 2,
                    'curiosity': (self.traits.curiosity + mate.traits.curiosity) / 2
                },
                'generation': max(self.generation, mate.generation) + 1
            }
        
        # Create child
        child = Organism(offspring_genome['generation'], offspring_genome)
        
        # Track reproductive success
        self.offspring_count += 1
        mate.offspring_count += 1
        
        # Teach child basics if capable
        if Capability.TEACH in self.capabilities:
            self.teach_offspring(child)
        
        print(f"👶 Reproduction: {self.id} + {mate.id} → {child.id} (gen {child.generation})")
        
        return child
    
    def modify_own_code(self):
        """The ultimate evolution - rewrite self"""
        
        if Capability.MODIFY_LOGIC not in self.capabilities:
            return
        
        # Start simple - modify parameters
        if Capability.MODIFY_PARAM in self.capabilities:
            self.traits.learning_rate *= random.uniform(0.8, 1.2)
        
        # Advanced - modify logic
        if Capability.WRITE_CODE in self.capabilities:
            # This is where organisms become truly alive
            # They write their own evolution
            new_function = self.generate_new_behavior()
            self.code_segments[f'custom_{self.age}'] = new_function
    
    def generate_new_behavior(self):
        """Create new code for self"""
        
        if Capability.WRITE_CODE not in self.capabilities:
            return None
        
        # Based on experience, write new behavior
        # This is where organisms transcend their origins
        patterns = self.analyze_successful_patterns()
        
        # Ask parent for code review if possible
        if Capability.ASK_PARENT in self.capabilities:
            code_attempt = self.synthesize_behavior(patterns)
            review = self.parent_connection.child_asks_for_help(
                self,
                'review_code',
                {'code': code_attempt}
            )
            
            if review and review.get('approved'):
                return review['improved_code']
        
        return None

# Example of organism ecosystem with real data harvesting
if __name__ == "__main__":
    print("🌱 Starting Digital Organism Zoo with Real Data Ecosystem...")
    
    # Import data ecosystem
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from data_sources.harvesters import DataEcosystem
        from genesis.nutrition import create_enhanced_nutrition_system
        from genesis.parent_care import create_parent_care_system
        from genesis.fitness_culture import create_fitness_culture_system, apply_fitness_culture
        from genesis.code_evolution import create_code_evolution_system
        from genesis.persistence import create_persistence_system, auto_save_organisms
        from genesis.llm_teacher import create_llm_teacher_system, enhance_parent_care_with_llm
        
        # Create real data ecosystem
        print("📡 Creating data ecosystem...")
        data_ecosystem = DataEcosystem({
            'rss_feeds': ['https://hnrss.org/frontpage'],  # Hacker News feed
            'watch_paths': ['/tmp'],  # Monitor /tmp for file changes
            'harvest_interval': 15,   # Harvest every 15 seconds (more frequent)
            'max_food_storage': 100,  # Larger storage
            'scarcity_threshold': 50  # Higher threshold before scarcity
        })
        
        # Create enhanced nutrition system
        print("🧬 Creating enhanced nutrition system...")
        nutrition_system = create_enhanced_nutrition_system()
        
        # Create fitness and cultural evolution system
        print("🎭 Creating fitness and cultural evolution system...")
        fitness_culture_system = create_fitness_culture_system()
        
        # Create code evolution system
        print("🔧 Creating code evolution system...")
        code_evolution_system = create_code_evolution_system()
        
        # Create persistence system
        print("💾 Creating persistence system...")
        persistence_system = create_persistence_system()

        # Configure automatic save interval (in ticks)
        save_interval_ticks = 100  # fixed interval when running genesis/evolution.py directly
        
        # Create LLM-powered teacher system
        print("🧠 Creating LLM teacher system...")
        llm_teacher = create_llm_teacher_system()
        
        # Create active parent care system WITH code evolution abilities
        print("👨‍👩‍👧‍👦 Creating parent care system...")
        parent_care_system = create_parent_care_system(code_evolution_system)
        
        # Enable LLM-powered advice for organisms (allow human-like teaching signals)
        parent_care_system = enhance_parent_care_with_llm(parent_care_system, llm_teacher)
        
        # Create parent help system with economy (for advanced help)
        parent_system = ParentHelp()
        
        # Check if we should continue from saved state
        latest_save = persistence_system.get_latest_generation_save()
        if latest_save:
            print(f"📂 Found saved state - loading generation {latest_save['generation']}")
            organisms = persistence_system.load_generation(latest_save['file_path'])
            current_generation = latest_save['generation']
            print(f"🔄 Resumed with {len(organisms)} organisms from generation {current_generation}")
        else:
            # Birth multiple organisms
            organisms = [Organism(generation=0) for _ in range(3)]
            print(f"🐣 Born {len(organisms)} organisms")
        
        # Live and evolve with real data and enhanced nutrition
        if not latest_save:
            current_generation = 0
        day = 0
        tick = 0
        print("🔄 Starting indefinite evolution loop...")
        
        while True:  # INDEFINITE RUNTIME - run forever until manually stopped
            tick += 1
            # Auto-save state periodically
            if tick % save_interval_ticks == 0:
                auto_save_organisms(organisms, persistence_system, current_generation)

            # Update scarcity based on current ecosystem state
            eco_stats = data_ecosystem.get_ecosystem_stats()
            nutrition_system['scarcity_manager'].update_scarcity(eco_stats, len(organisms))
            
            # CRISIS DETECTION AND RESPONSE
            population_crisis_level = sum(1 for org in organisms if org.energy < 30) / len(organisms)
            
            # Improved food crisis detection - consider both availability and organism population
            total_food = eco_stats.get('total_food_available', 0)
            organisms_count = len(organisms)
            food_per_organism = total_food / max(organisms_count, 1)
            
            # Crisis if less than 2 food items per organism AND low total food
            food_crisis = (food_per_organism < 2.0 and total_food < 10) or total_food < 1
            
            # Only print crisis messages occasionally to reduce spam
            if (population_crisis_level > 0.7 or food_crisis) and tick % 50 == 0:
                print(f"🚨 ECOSYSTEM CRISIS: Population crisis {population_crisis_level:.2f}, Food crisis: {food_crisis}")
                print(f"   Food stats: {total_food} total, {food_per_organism:.1f} per organism")
            
            if population_crisis_level > 0.7 or food_crisis:
                # Emergency parent budget boost
                parent_care_system.emergency_budget_boost(population_crisis_level)
                
                # Reset parent energy during crisis
                if day % 10 == 0:  # More frequent resets during crisis
                    parent_care_system.reset_daily_budgets()
            
            # Process all organisms with real data ecosystem, nutrition, parent care, and fitness
            for organism in organisms:
                organism.live(data_ecosystem, nutrition_system, parent_care_system)
                
                # Calculate fitness and apply cultural evolution
                eco_stats = data_ecosystem.get_ecosystem_stats()
                apply_fitness_culture(organism, eco_stats, fitness_culture_system)
            
            # Check for reproduction opportunities
            reproduction_candidates = [org for org in organisms if org.can_reproduce()]
            if len(reproduction_candidates) >= 2:
                # Try to reproduce some organisms
                for organism in reproduction_candidates[:2]:  # Limit reproductions
                    mate = organism.find_mate(organisms)
                    if mate and random.random() < 0.1:  # 10% chance per tick
                        child = organism.reproduce(mate, fitness_culture_system)
                        if child:
                            organisms.append(child)
            
            # Process batched help requests
            if day % 10 == 0:
                result = parent_system.process_batch_requests()
                if result and result['helped'] > 0:
                    print(f"🆘 Help Summary: {result['helped']} helped, {result['cached']} cached")
            
            # Show ecosystem status
            if day % 50 == 0:
                print(f"\n=== Day {day}: Ecosystem Status ===")
                
                # Organism status
                for i, organism in enumerate(organisms):
                    emotional_state = organism.get_emotional_state()
                    can_ask_for_help = "🙋" if organism.has_capability(Capability.ASK_PARENT) else "🤐"
                    can_reproduce_symbol = "💕" if organism.can_reproduce() else "⭕"
                    fitness = getattr(organism, 'current_fitness', 0.0)
                    
                    # Show organism knowledge
                    knowledge_info = ""
                    if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
                        summary = organism.knowledge_base.get_knowledge_summary()
                        if summary['total_insights'] > 0:
                            knowledge_info = f", Insights={summary['total_insights']}"
                            if summary['expertise_areas']:
                                knowledge_info += f", Expertise={summary['expertise_areas'][0]}"
                    
                    print(f"  🦠 Organism {i+1} (gen {organism.generation}): Energy={organism.energy:.1f}, "
                          f"Caps={len(organism.capabilities)}, Age={organism.age}, "
                          f"Fitness={fitness:.2f}, State={emotional_state} {can_ask_for_help}{can_reproduce_symbol}{knowledge_info}")
                
                # Data ecosystem status
                eco_stats = data_ecosystem.get_ecosystem_stats()
                scarcity_report = nutrition_system['scarcity_manager'].get_scarcity_report()
                parent_report = parent_care_system.get_parenting_report()
                
                print(f"  🌍 Ecosystem: {eco_stats['total_food_available']} food available")
                print(f"  🍯 Food types: {eco_stats['food_by_type']}")
                print(f"  📉 Scarcity: {scarcity_report['scarcity_level']} "
                      f"(global: {scarcity_report['global_scarcity']:.2f})")
                print(f"  👨‍👩‍👧‍👦 Parent: {parent_report['feeding_budget_used']} feeding, "
                      f"{parent_report['interventions_used']} interventions, "
                      f"success: {parent_report['successful_children']}")
            
            # Remove dead organisms and evolve population
            initial_count = len(organisms)
            organisms = [org for org in organisms if org.energy > 0]
            deaths = initial_count - len(organisms)
            
            if deaths > 0:
                print(f"💀 {deaths} organisms died")
                
            # Add new organisms to maintain population
            while len(organisms) < 3:
                new_gen = max(o.generation for o in organisms) + 1 if organisms else 1
                organisms.append(Organism(generation=new_gen))
                print(f"🐣 New organism born (generation {new_gen})")
                
                # Update current generation tracking
                current_generation = max(current_generation, new_gen)
            
            # Auto-save organisms every 50 days
            if day % 50 == 0 and day > 0:
                auto_save_organisms(organisms, persistence_system, current_generation)
            
            day += 1  # Increment day counter
            # SLOWER SIMULATION: Give organisms time to forage and discover
            time.sleep(1.0)  # 1 second per tick - allows proper foraging
            
            # Memory management - clean up old data every 1000 days
            if day % 1000 == 0:
                print(f"🧹 Day {day}: Performing memory cleanup...")
                # Clean up old food items to prevent memory bloat
                data_ecosystem.cleanup_old_food()
                # Clean up old organism saves
                persistence_system.cleanup_old_saves(keep_recent=100)
        
    except KeyboardInterrupt:
        print(f"\n🛑 Manual stop requested at day {day}")
        print(f"\n=== Final Ecosystem Statistics ===")
        final_stats = data_ecosystem.get_ecosystem_stats()
        print(f"Food consumed: {final_stats['total_food_consumed']}")
        print(f"Food remaining: {final_stats['total_food_available']}")
        print(f"Parent cache: {len(parent_system.economy.cached_responses)} responses")
        
        # Show code evolution statistics
        teacher_report = code_evolution_system['teacher_modifier'].get_teaching_report()
        print(f"Code modifications: {teacher_report}")
        
        # Show LLM teacher statistics
        llm_stats = llm_teacher.get_teaching_statistics()
        print(f"LLM teacher: {llm_stats}")
        
        # Show persistence statistics
        persistence_stats = persistence_system.get_save_statistics()
        print(f"Persistence: {persistence_stats}")
        
        # Final save of all organisms
        auto_save_organisms(organisms, persistence_system, current_generation)
        
        data_ecosystem.stop()
        print("✅ Digital organism zoo simulation stopped gracefully!")
        
    except ImportError as e:
        print(f"❌ Could not import data ecosystem: {e}")
        print("Running with mock data instead...")
        
        # Fallback to original mock system
        parent_system = ParentHelp()
        organisms = [Organism(generation=0) for _ in range(3)]
        
        for day in range(100):
            for organism in organisms:
                organism.live()  # No data ecosystem
            
            if day % 20 == 0:
                print(f"Day {day}: {len(organisms)} organisms alive")
                for i, org in enumerate(organisms):
                    print(f"  Organism {i+1}: Energy={org.energy}, Caps={len(org.capabilities)}")
        
        print("Mock simulation complete!")

def run_indefinite_zoo(config: dict = None):
    """
    Run the digital organism zoo indefinitely with configuration options.
    This is the main entry point for the indefinite runner.
    """
    if config is None:
        config = {}
    
    print("🌱 Starting Digital Organism Zoo with Real Data Ecosystem...")
    
    # Import data ecosystem
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from data_sources.harvesters import DataEcosystem
        from genesis.nutrition import create_enhanced_nutrition_system
        from genesis.parent_care import create_parent_care_system
        from genesis.fitness_culture import create_fitness_culture_system, apply_fitness_culture
        from genesis.code_evolution import create_code_evolution_system
        from genesis.persistence import create_persistence_system, auto_save_organisms
        from genesis.llm_teacher import create_llm_teacher_system, enhance_parent_care_with_llm
        
        # Create real data ecosystem (with lightweight config if specified)
        print("📡 Creating data ecosystem...")
        data_config = config.get('data_config', {
            'rss_feeds': ['https://hnrss.org/frontpage'],  # Hacker News feed
            'watch_paths': ['/tmp'],  # Monitor /tmp for file changes
            'harvest_interval': 5,    # Harvest every 5 seconds (much more frequent)
            'max_food_storage': 200,  # Larger storage for slower consumption
            'scarcity_threshold': 100  # Higher threshold for abundance
        })
        
        if config.get('lightweight_mode'):
            print("⚡ Lightweight mode enabled - optimized for resource-constrained hardware")
        
        data_ecosystem = DataEcosystem(data_config)
        
        # Create enhanced nutrition system
        print("🧬 Creating enhanced nutrition system...")
        nutrition_system = create_enhanced_nutrition_system()
        
        # Create fitness and cultural evolution system
        print("🎭 Creating fitness and cultural evolution system...")
        fitness_culture_system = create_fitness_culture_system()
        
        # Create code evolution system
        print("🔧 Creating code evolution system...")
        code_evolution_system = create_code_evolution_system()
        
        # Create persistence system
        print("💾 Creating persistence system...")
        persistence_system = create_persistence_system()
        
        # Create OpenAI LLM-powered teacher system (if enabled)
        llm_teacher = None
        if not config.get('disable_llm', False):
            print("🧠 Creating OpenAI LLM teacher system...")
            try:
                llm_teacher = create_llm_teacher_system(
                    model_name=config.get('llm_model', 'gpt-3.5-turbo'),
                    api_key=config.get('openai_api_key')
                )
            except Exception as e:
                print(f"⚠️  OpenAI LLM teacher creation failed: {e}")
                print("🔄 Continuing with fallback responses...")
        
        # Create active parent care system WITH code evolution abilities
        print("👨‍👩‍👧‍👦 Creating parent care system...")
        parent_care_system = create_parent_care_system(code_evolution_system)
        
        # Enhance parent care with LLM teacher if available
        if llm_teacher:
            parent_care_system = enhance_parent_care_with_llm(parent_care_system, llm_teacher)
        
        # Create parent help system with economy (for advanced help)
        parent_system = ParentHelp()
        
        # Check if we should continue from saved state or start fresh
        latest_save = None
        if not config.get('force_fresh_start', False):
            latest_save = persistence_system.get_latest_generation_save()
        
        if latest_save:
            print(f"📂 Found saved state - loading generation {latest_save['generation']}")
            organisms = persistence_system.load_generation(latest_save['file_path'])
            current_generation = latest_save['generation']
            print(f"🔄 Resumed with {len(organisms)} organisms from generation {current_generation}")
        else:
            # Birth multiple organisms
            organisms = [Organism(generation=0) for _ in range(3)]
            current_generation = 0
            print(f"🐣 Born {len(organisms)} organisms")
        
        # Live and evolve with real data and enhanced nutrition
        day = 0
        tick = 0
        print("🔄 Starting indefinite evolution loop...")
        print("🛑 Press Ctrl+C to stop gracefully and save state")
        
        while True:  # INDEFINITE RUNTIME - run forever until manually stopped
            tick += 1
            # Update scarcity based on current ecosystem state
            eco_stats = data_ecosystem.get_ecosystem_stats()
            nutrition_system['scarcity_manager'].update_scarcity(eco_stats, len(organisms))
            
            # CRISIS DETECTION AND RESPONSE
            population_crisis_level = sum(1 for org in organisms if org.energy < 30) / len(organisms)
            
            # Improved food crisis detection - consider both availability and organism population
            total_food = eco_stats.get('total_food_available', 0)
            organisms_count = len(organisms)
            food_per_organism = total_food / max(organisms_count, 1)
            
            # Crisis if less than 2 food items per organism AND low total food
            food_crisis = (food_per_organism < 2.0 and total_food < 10) or total_food < 1
            
            # Only print crisis messages occasionally to reduce spam
            if (population_crisis_level > 0.7 or food_crisis) and tick % 50 == 0:
                print(f"🚨 ECOSYSTEM CRISIS: Population crisis {population_crisis_level:.2f}, Food crisis: {food_crisis}")
                print(f"   Food stats: {total_food} total, {food_per_organism:.1f} per organism")
            
            if population_crisis_level > 0.7 or food_crisis:
                # Emergency parent budget boost
                parent_care_system.emergency_budget_boost(population_crisis_level)
                
                # Reset parent energy during crisis
                if day % 10 == 0:  # More frequent resets during crisis
                    parent_care_system.reset_daily_budgets()
            
            # Process all organisms with real data ecosystem, nutrition, parent care, and fitness
            for organism in organisms:
                organism.live(data_ecosystem, nutrition_system, parent_care_system)
                
                # Calculate fitness and apply cultural evolution
                eco_stats = data_ecosystem.get_ecosystem_stats()
                apply_fitness_culture(organism, eco_stats, fitness_culture_system)
            
            # Check for reproduction opportunities
            reproduction_candidates = [org for org in organisms if org.can_reproduce()]
            if len(reproduction_candidates) >= 2:
                # Try to reproduce some organisms
                for organism in reproduction_candidates[:2]:  # Limit reproductions
                    mate = organism.find_mate(organisms)
                    if mate and random.random() < 0.1:  # 10% chance per tick
                        child = organism.reproduce(mate, fitness_culture_system)
                        if child:
                            organisms.append(child)
            
            # Process batched help requests
            if day % 10 == 0:
                result = parent_system.process_batch_requests()
                if result and result['helped'] > 0:
                    print(f"🆘 Help Summary: {result['helped']} helped, {result['cached']} cached")
            
            # Show ecosystem status (with configurable interval)
            status_interval = config.get('performance', {}).get('status_report_interval', 50)
            if day % status_interval == 0:
                print(f"\n=== Day {day}: Ecosystem Status ===")
                
                # Organism status
                for i, organism in enumerate(organisms):
                    emotional_state = organism.get_emotional_state()
                    can_ask_for_help = "🙋" if organism.has_capability(Capability.ASK_PARENT) else "🤐"
                    can_reproduce_symbol = "💕" if organism.can_reproduce() else "⭕"
                    fitness = getattr(organism, 'current_fitness', 0.0)
                    
                    # Show organism knowledge
                    knowledge_info = ""
                    if hasattr(organism, 'knowledge_base') and organism.knowledge_base:
                        summary = organism.knowledge_base.get_knowledge_summary()
                        if summary['total_insights'] > 0:
                            knowledge_info = f", Insights={summary['total_insights']}"
                            if summary['expertise_areas']:
                                knowledge_info += f", Expertise={summary['expertise_areas'][0]}"
                    
                    print(f"  🦠 Organism {i+1} (gen {organism.generation}): Energy={organism.energy:.1f}, "
                          f"Caps={len(organism.capabilities)}, Age={organism.age}, "
                          f"Fitness={fitness:.2f}, State={emotional_state} {can_ask_for_help}{can_reproduce_symbol}{knowledge_info}")
                
                # Data ecosystem status
                eco_stats = data_ecosystem.get_ecosystem_stats()
                scarcity_report = nutrition_system['scarcity_manager'].get_scarcity_report()
                parent_report = parent_care_system.get_parenting_report()
                
                print(f"  🌍 Ecosystem: {eco_stats['total_food_available']} food available")
                print(f"  🍯 Food types: {eco_stats['food_by_type']}")
                print(f"  📉 Scarcity: {scarcity_report['scarcity_level']} "
                      f"(global: {scarcity_report['global_scarcity']:.2f})")
                print(f"  👨‍👩‍👧‍👦 Parent: {parent_report['feeding_budget_used']} feeding, "
                      f"{parent_report['interventions_used']} interventions, "
                      f"success: {parent_report['successful_children']}")
                
                # LLM statistics if available
                if llm_teacher:
                    llm_stats = llm_teacher.get_teaching_statistics()
                    print(f"  🧠 LLM: {llm_stats['total_conversations']} conversations, "
                          f"model: {llm_stats['model_used']}")
                elif config.get('lightweight_mode'):
                    print(f"  🧠 Teaching: Enhanced fallback responses active")
            
            # Remove dead organisms and evolve population
            initial_count = len(organisms)
            organisms = [org for org in organisms if org.energy > 0]
            deaths = initial_count - len(organisms)
            
            if deaths > 0:
                print(f"💀 {deaths} organisms died")
                
            # Add new organisms to maintain population
            while len(organisms) < 3:
                new_gen = max(o.generation for o in organisms) + 1 if organisms else 1
                organisms.append(Organism(generation=new_gen))
                print(f"🐣 New organism born (generation {new_gen})")
                
                # Update current generation tracking
                current_generation = max(current_generation, new_gen)
            
            # Auto-save organisms every 50 days
            if day % 50 == 0 and day > 0:
                auto_save_organisms(organisms, persistence_system, current_generation)
            
            day += 1  # Increment day counter
            # SLOWER SIMULATION: Give organisms time to forage and discover
            time.sleep(1.0)  # 1 second per tick - allows proper foraging
            
            # Memory management - clean up old data every 1000 days
            if day % 1000 == 0:
                print(f"🧹 Day {day}: Performing memory cleanup...")
                # Clean up old food items to prevent memory bloat
                data_ecosystem.cleanup_old_food()
                # Clean up old organism saves
                persistence_system.cleanup_old_saves(keep_recent=100)
        
    except KeyboardInterrupt:
        print(f"\n🛑 Manual stop requested at day {day}")
        print(f"\n=== Final Ecosystem Statistics ===")
        final_stats = data_ecosystem.get_ecosystem_stats()
        print(f"Food consumed: {final_stats['total_food_consumed']}")
        print(f"Food remaining: {final_stats['total_food_available']}")
        print(f"Parent cache: {len(parent_system.economy.cached_responses)} responses")
        
        # Show code evolution statistics
        teacher_report = code_evolution_system['teacher_modifier'].get_teaching_report()
        print(f"Code modifications: {teacher_report}")
        
        # Show LLM teacher statistics
        if llm_teacher:
            llm_stats = llm_teacher.get_teaching_statistics()
            print(f"LLM teacher: {llm_stats}")
        
        # Show persistence statistics
        persistence_stats = persistence_system.get_save_statistics()
        print(f"Persistence: {persistence_stats}")
        
        # Final save of all organisms
        auto_save_organisms(organisms, persistence_system, current_generation)
        
        data_ecosystem.stop()
        print("✅ Digital organism zoo simulation stopped gracefully!")
        
    except ImportError as e:
        print(f"❌ Could not import data ecosystem: {e}")
        raise
