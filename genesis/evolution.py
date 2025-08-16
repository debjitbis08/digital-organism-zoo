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
    """A digital life form that evolves"""
    
    def __init__(self, generation=0, parent_genome=None):
        self.id = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        self.generation = generation
        self.age = 0
        self.energy = 100
        self.traits = EvolvableTraits()
        self.capabilities = {Capability.SENSE_DATA, Capability.EAT_TEXT}
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
    
    def process_environment(self, environment):
        """Handle environment that organism can process"""
        if environment['type'] == 'real_food':
            # Process real data morsel
            morsel = environment['morsel']
            energy_gained = morsel.energy_value
            self.energy += energy_gained
            self.memory.append(f"ate_{morsel.data_type.value}:{morsel.source}")
            self.consecutive_failures = 0
            print(f"🍽️  Organism {self.id} ate {morsel.data_type.value} from {morsel.source} (+{energy_gained} energy)")
            
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
    
    def live(self, data_ecosystem=None):
        """One moment of existence"""
        
        self.age += 1
        self.energy -= 1  # Constant drain
        
        # Try to survive
        environment = self.sense_environment(data_ecosystem)
        
        # Can I handle this?
        if self.can_process(environment):
            self.process_environment(environment)
        else:
            # Failed to process - track failure and maybe learn to ask for help
            self.process_environment(environment)  # This will increment frustration
            
            # Check if organism should discover ASK_PARENT capability
            self.check_frustration_based_learning()
            
            # Ask parent for help if capable
            if self.has_capability(Capability.ASK_PARENT):
                self.ask_for_help(environment)
            else:
                # Struggle silently, building frustration
                self.energy -= 3  # Extra energy cost for struggling
        
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
    
    def reproduce(self):
        """Create offspring with mutations"""
        
        if self.energy < 150:
            # Need excess energy to reproduce
            if Capability.ASK_PARENT in self.capabilities:
                self.parent_connection.child_asks_for_help(
                    self,
                    'want_reproduce',
                    {'energy': self.energy}
                )
            return None
        
        # Create child
        child_genome = self.create_genome()
        child = Organism(self.generation + 1, child_genome)
        
        # Teach child basics
        if Capability.TEACH in self.capabilities:
            self.teach_offspring(child)
        
        self.energy -= 50  # Cost of reproduction
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
        
        # Create real data ecosystem
        print("📡 Creating data ecosystem...")
        data_ecosystem = DataEcosystem({
            'rss_feeds': ['https://hnrss.org/frontpage'],  # Hacker News feed
            'watch_paths': ['/tmp'],  # Monitor /tmp for file changes
            'harvest_interval': 30,   # Harvest every 30 seconds
            'max_food_storage': 50
        })
        
        # Create parent help system with economy
        parent_system = ParentHelp()
        
        # Birth multiple organisms
        organisms = [Organism(generation=0) for _ in range(3)]
        print(f"🐣 Born {len(organisms)} organisms")
        
        # Live and evolve with real data
        for day in range(200):
            # Process all organisms with real data ecosystem
            for organism in organisms:
                organism.live(data_ecosystem)
            
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
                    print(f"  🦠 Organism {i+1}: Energy={organism.energy}, "
                          f"Caps={len(organism.capabilities)}, "
                          f"State={emotional_state} {can_ask_for_help}")
                
                # Data ecosystem status
                eco_stats = data_ecosystem.get_ecosystem_stats()
                print(f"  🌍 Ecosystem: {eco_stats['total_food_available']} food available, "
                      f"scarcity={eco_stats['food_scarcity']:.2f}")
                print(f"  🍯 Food types: {eco_stats['food_by_type']}")
            
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
            
            time.sleep(0.1)  # Small delay to see output
        
        print(f"\n=== Final Ecosystem Statistics ===")
        final_stats = data_ecosystem.get_ecosystem_stats()
        print(f"Food consumed: {final_stats['total_food_consumed']}")
        print(f"Food remaining: {final_stats['total_food_available']}")
        print(f"Parent cache: {len(parent_system.economy.cached_responses)} responses")
        
        data_ecosystem.stop()
        print("✅ Digital organism zoo simulation complete!")
        
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