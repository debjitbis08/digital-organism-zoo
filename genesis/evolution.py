# Organism Evolution System: What Can Evolve & Parent-Help Mechanism

import json
import os
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
        try:
            from genesis.stream import doom_feed
            doom_feed.add('parent_help', f"cached tip for {request.organism_id}", 1)
        except Exception:
            pass
    
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
        try:
            from genesis.stream import doom_feed
            doom_feed.add('parent_help', f"new advice for {request.organism_id}", 2)
        except Exception:
            pass
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
        try:
            from genesis.stream import doom_feed
            doom_feed.add('parent_refusal', f"{request.organism_id}: {message}", 2)
        except Exception:
            pass

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

# Simple shared trade board for exchanging foraging leads
class _TradeBoard:
    def __init__(self, max_items: int = 50):
        self.max_items = max_items
        self.leads: List[Dict[str, Any]] = []

    def post_lead(self, organism_id: str, food_type, source: str, score: float = 1.0, hint: Optional[str] = None, region: Optional[str] = None):
        try:
            entry = {
                'organism': organism_id,
                'type': food_type,  # DataType enum
                'source': source,
                'score': float(score),
                'ts': time.time(),
                'hint': hint or '',
                'region': region or '',
            }
            self.leads.append(entry)
            if len(self.leads) > self.max_items:
                self.leads = self.leads[-self.max_items:]
            from genesis.stream import doom_feed
            kind = getattr(food_type, 'value', str(food_type)) if food_type is not None else (hint or 'hint')
            region_tag = f" [{region}]" if region else ''
            doom_feed.add('lead', f"{organism_id} posted lead: {kind} from {source}{region_tag}", 1, {'organism': organism_id})
        except Exception:
            pass

    def get_recent_leads(self, limit: int = 5) -> List[Dict[str, Any]]:
        return list(self.leads[-limit:])


# Singleton trade board
trade_board = _TradeBoard()

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
        
        # Initialize simple evolvable brain
        try:
            from genesis.brain import BrainGenome, Brain
            self.brain_genome = BrainGenome.random()
            self.brain = Brain(self.brain_genome)
        except Exception:
            self.brain_genome = None
            self.brain = None
        
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
        self._milestones = set()
        # Social signals reinforcement tracking
        self.trade_lead_successes = 0
        self.hint_lead_successes = 0
        # Virtual region for lightweight migration experiments
        self.current_region = 'default'
        # Interface adaptation dynamics
        self.interface_adaptation_rate = 0.25
        self._adaptation_history = []  # recent outcomes for tuning
        
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
        # Simple inheritance - copy selected traits and mutate slightly
        try:
            parent_traits = parent_genome.get('traits', {}) if isinstance(parent_genome, dict) else {}
            # Copy over numeric traits when present
            for attr, val in parent_traits.items():
                if hasattr(self.traits, attr) and isinstance(val, (int, float)):
                    # Small mutation around parent value
                    jitter = random.uniform(0.95, 1.05)
                    setattr(self.traits, attr, float(val) * jitter)

            # Inherit a subset of capabilities if provided
            caps = parent_genome.get('capabilities') if isinstance(parent_genome, dict) else None
            if caps:
                try:
                    from genesis.evolution import Capability
                    inherited = set(Capability(c) if not isinstance(c, Capability) else c for c in caps)
                    # Keep always-on basics, add inherited set
                    self.capabilities = set(self.capabilities) | inherited
                except Exception:
                    # If capability parsing fails, ignore and keep defaults
                    pass

            # Advance generation if present
            if isinstance(parent_genome, dict) and 'generation' in parent_genome:
                self.generation = int(parent_genome['generation'])
        except Exception:
            # Best-effort inheritance; fall back to defaults on error
            return
    
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
        
        # Use brain to derive simple drives from state + ecosystem + nutrition
        self._compute_brain_drives(data_ecosystem, nutrition_system)
        
        # Number of foraging attempts based on capabilities and desperation
        base_attempts = 1
        if self.has_capability(Capability.PATTERN_MATCH):
            base_attempts += 1  # Pattern matching = better foraging
        if self.has_capability(Capability.REMEMBER):
            base_attempts += 1  # Memory = learn good spots
        if self.energy < 30:
            base_attempts += 2  # Desperation = more searching
        # Brain exploration drive gives bonus attempts
        if getattr(self, '_brain_drives', None):
            exp = self._brain_drives.get('explore', 0.0)
            if exp > 0.5:
                base_attempts += 1
            if exp > 0.8:
                base_attempts += 1
            # High conserve drive reduces unnecessary searching when safe
            if self.energy > 40 and self._brain_drives.get('conserve', 0.0) > 0.8:
                base_attempts = max(1, base_attempts - 1)
        # Competition-aware adjustment using last sensor snapshot (higher scarcity/competition -> try a bit harder)
        try:
            comp = 0.0
            if hasattr(self, '_last_sensor_map'):
                comp = float(self._last_sensor_map.get('competition_local', 0.0))
            if comp > 0.75 and base_attempts < 4:
                base_attempts += 1
            elif comp < 0.25 and base_attempts > 1 and getattr(self, '_brain_drives', {}).get('conserve', 0.0) > 0.6:
                base_attempts = max(1, base_attempts - 1)
        except Exception:
            pass
        # Migration action: switch virtual regions when scarcity and drive are high
        if getattr(self, '_brain_drives', None):
            mig = self._brain_drives.get('migrate', 0.0)
            try:
                eco = data_ecosystem.get_ecosystem_stats() if data_ecosystem else {}
                scarcity_flag = (eco.get('food_scarcity', 1.0) or 1.0) < 0.5
            except Exception:
                scarcity_flag = False
            force_mig = os.environ.get('ZOO_FORCE_MIGRATION', '0') == '1'
            if force_mig or (mig > 0.75 and scarcity_flag and random.random() < 0.25):
                prev = self.current_region
                # Choose destination based on other drives
                drives = self._brain_drives
                target = prev
                if drives.get('prefer_structured', 0.0) > 0.6:
                    target = 'structured-rich'
                elif drives.get('risk', 0.0) > 0.7:
                    target = 'code-rich'
                elif drives.get('conserve', 0.0) > 0.6:
                    target = 'text-meadow'
                if target == prev and force_mig:
                    # Pick an alternate region deterministically for testing
                    try:
                        # Use known regions from ecosystem biases
                        regions = ['structured-rich', 'code-rich', 'text-meadow']
                        target = regions[0] if prev not in regions else regions[(regions.index(prev) + 1) % len(regions)]
                    except Exception:
                        target = 'structured-rich'
                if target != prev:
                    self.current_region = target
                    try:
                        from genesis.stream import doom_feed
                        doom_feed.add('migration', f"{self.id} migrated {prev}→{target}", 2, {'organism': self.id})
                    except Exception:
                        pass
        
        successful_forages = 0
        foraging_patterns = []
        
        for attempt in range(base_attempts):
            # Each attempt is an evolutionary exploration
            food_found = self._explore_for_food(data_ecosystem, attempt, nutrition_system)
            
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

    def _compute_brain_drives(self, data_ecosystem=None, nutrition_system=None):
        """Run the organism's brain to compute simple behavior drives.
        Produces a dict with keys like 'explore' and 'social'.
        """
        if not self.brain:
            self._brain_drives = None
            return
        # Build input vector from brain sensors gene list
        energy_norm = max(0.0, min(1.0, self.energy / 100.0))
        frustration = max(0.0, min(1.0, getattr(self, 'frustration', 0.0)))
        memory_load = max(0.0, min(1.0, len(self.memory) / 100.0))
        scarcity = 1.0
        if data_ecosystem:
            eco = data_ecosystem.get_ecosystem_stats()
            scarcity = 1.0 - max(0.0, min(1.0, eco.get('food_scarcity', 1.0)))
        age_norm = max(0.0, min(1.0, self.age / 500.0))
        cap_norm = max(0.0, min(1.0, len(self.capabilities) / 10.0))
        recent_success = getattr(self, 'foraging_success_rate', 0.5)
        sensor_map = {
            'energy': energy_norm,
            'frustration': frustration,
            'memory_load': memory_load,
            'scarcity': scarcity,
            'age': age_norm,
            'capability_density': cap_norm,
            'recent_success': max(0.0, min(1.0, recent_success)),
        }
        # Extended sensors available for Task 5
        # Global scarcity (alias)
        sensor_map['scarcity_global'] = scarcity
        # Ecosystem-derived
        if data_ecosystem:
            eco = data_ecosystem.get_ecosystem_stats()
            avg_fresh = eco.get('average_freshness', 0.5) or 0.5
            fbt = eco.get('food_by_type', {})
            total = sum(fbt.values()) or 1
            availability_structured = fbt.get('structured_json', 0) / total
            availability_code = fbt.get('code', 0) / total
            sensor_map['freshness_expectation'] = max(0.0, min(1.0, avg_fresh))
            sensor_map['availability_structured'] = max(0.0, min(1.0, availability_structured))
            sensor_map['availability_code'] = max(0.0, min(1.0, availability_code))
            # Type-specific scarcity proxies
            sensor_map['scarcity_structured'] = max(0.0, min(1.0, 1.0 - availability_structured))
            sensor_map['scarcity_code'] = max(0.0, min(1.0, 1.0 - availability_code))
            # Competition/pressure: blend scarcity with regional population size if available
            comp = scarcity
            if hasattr(self, '_region_population'):
                # Map 1..6+ population to ~0..1
                comp = max(comp, max(0.0, min(1.0, (float(self._region_population) - 1.0) / 5.0)))
            sensor_map['competition_local'] = max(0.0, min(1.0, comp))
        # Metabolic/health
        if nutrition_system and 'metabolic_tracker' in nutrition_system:
            prof = nutrition_system['metabolic_tracker'].metabolic_profiles.get(self.id)
            if prof:
                sensor_map['toxicity_buildup'] = max(0.0, min(1.0, prof.get('toxin_buildup', 0.0)))
                me = prof.get('metabolic_efficiency', 1.0)  # ~0.3..1.0
                # Normalize approx 0..1
                sensor_map['metabolic_efficiency'] = max(0.0, min(1.0, (me - 0.3) / 0.7))
        # Novelty desire: stronger when recent success is low
        sensor_map['novelty_hunger'] = max(0.0, min(1.0, 1.0 - sensor_map.get('recent_success', 0.5)))
        # Keep last sensor snapshot for downstream preference logic
        self._last_sensor_map = sensor_map
        sensors = getattr(self.brain, 'sensors', ['energy','frustration','memory_load','scarcity','age','capability_density'])
        inputs = [sensor_map.get(s, 0.0) for s in sensors]
        try:
            outputs = self.brain.forward(inputs)
            # Map outputs to [0,1] via simple squashing in actuator order
            def squash(x):
                return max(0.0, min(1.0, 0.5 + (x / 4.0)))
            actuators = getattr(self.brain, 'actuators', ['explore','social','conserve','prefer_structured','risk','teach','trade','migrate'])
            drives = {}
            for i, name in enumerate(actuators):
                val = outputs[i] if i < len(outputs) else 0.0
                drives[name] = squash(val)
            self._brain_drives = drives
            # Occasionally surface high-level intent in the doom feed for readability
            try:
                if random.random() < 0.05:
                    from genesis.stream import doom_feed
                    top = sorted(drives.items(), key=lambda kv: kv[1], reverse=True)
                    if top:
                        k, v = top[0]
                        doom_feed.add('intent', f"{self.id} drive: {k}={v:.2f}", 1, {'organism': self.id})
            except Exception:
                pass
        except Exception:
            self._brain_drives = None

    def _get_interface_adapt_rate(self) -> float:
        """Dynamic probability to adapt interfaces based on recent performance.

        Higher when struggling; lower when succeeding to stabilize beneficial I/O.
        """
        base = getattr(self, 'interface_adaptation_rate', 0.25)
        fsr = getattr(self, 'foraging_success_rate', 0.5)
        # Struggling: increase chance to adapt
        if fsr < 0.3 or self.energy < 50:
            base = min(0.6, base + 0.2)
        # Succeeding: reduce chance to adapt (stabilize)
        elif fsr > 0.55 and self.energy > 80:
            base = max(0.05, base - 0.15)
        # Toxicity high -> slight increase to add metabolic sensors
        try:
            tox = 0.0
            if hasattr(self, '_last_sensor_map'):
                tox = float(self._last_sensor_map.get('toxicity_buildup', 0.0))
            if tox > 0.6:
                base = min(0.6, base + 0.1)
        except Exception:
            pass
        return base
    
    def _explore_for_food(self, data_ecosystem, attempt_number, nutrition_system=None):
        """Single foraging exploration attempt"""
        # Use a weighted preference strategy derived from drives and memory
        from data_sources.harvesters import DataType

        preferred_types = self._choose_preferred_types(n=2, data_ecosystem=data_ecosystem, nutrition_system=nutrition_system)

        # Different exploration strategies based on attempt number
        if attempt_number == 0:
            # Build preferences informed by brain drives and metabolic state
            prefs = {'preferred_types': preferred_types} if preferred_types else {}
            drives = getattr(self, '_brain_drives', {}) or {}
            # Difficulty: conserve prefers easy, risk prefers challenging
            if drives.get('conserve', 0.0) > 0.6 and drives.get('risk', 0.0) < 0.6:
                prefs['difficulty_preference'] = 'low'
            elif drives.get('risk', 0.0) > 0.7 and drives.get('conserve', 0.0) < 0.6:
                prefs['difficulty_preference'] = 'high'
            # Metabolic efficiency nudges difficulty
            try:
                me = 0.7
                if hasattr(self, '_last_sensor_map'):
                    me = max(0.0, min(1.0, float(self._last_sensor_map.get('metabolic_efficiency', 0.7))))
                if me < 0.4:
                    prefs['difficulty_preference'] = 'low'
                elif me > 0.8 and drives.get('risk', 0.0) > 0.6:
                    prefs['difficulty_preference'] = 'high'
            except Exception:
                pass
            # Apply region preference to leverage virtual habitats
            try:
                if hasattr(self, 'current_region') and self.current_region:
                    prefs['region'] = self.current_region
            except Exception:
                pass
            # Freshness threshold influenced by conserve
            cons = drives.get('conserve', 0.0)
            min_fresh = max(0.0, min(1.0, 0.2 + 0.5 * cons))
            # Auto-tune with ecosystem freshness expectation
            try:
                eco_stats = data_ecosystem.get_ecosystem_stats()
                avg_fresh = eco_stats.get('average_freshness', 0.5) or 0.5
                min_fresh = max(min_fresh, max(0.0, min(1.0, avg_fresh - 0.1)))
            except Exception:
                pass
            # Novelty hunger reduces freshness threshold slightly to explore more
            try:
                novelty = 0.0
                if hasattr(self, '_last_sensor_map'):
                    novelty = max(0.0, min(1.0, float(self._last_sensor_map.get('novelty_hunger', 0.0))))
                if novelty > 0.5:
                    min_fresh = max(0.0, min_fresh - 0.1 * (novelty - 0.5) * 2.0)
            except Exception:
                pass
            prefs['min_freshness'] = min_fresh
            # Toxicity avoidance based on metabolic profile
            if nutrition_system and 'metabolic_tracker' in nutrition_system:
                mt = nutrition_system['metabolic_tracker']
                prof = mt.metabolic_profiles.get(self.id)
                if prof and prof.get('toxin_buildup', 0.0) > 0.6:
                    prefs['toxicity_avoid_code'] = True
            # Competition-aware freshness tuning: under high competition, be less picky; under low + conserve, be pickier
            try:
                comp = 0.0
                if hasattr(self, '_last_sensor_map'):
                    comp = max(0.0, min(1.0, float(self._last_sensor_map.get('competition_local', 0.0))))
                if comp > 0.7:
                    prefs['min_freshness'] = max(0.0, prefs.get('min_freshness', 0.0) - 0.05 * (comp - 0.7) * 3.0)
                elif comp < 0.3 and drives.get('conserve', 0.0) > 0.6:
                    prefs['min_freshness'] = min(1.0, prefs.get('min_freshness', 0.0) + 0.05)
            except Exception:
                pass
            # Use trade board lead to bias first attempt if available
            if drives.get('trade', 0.0) > 0.6:
                leads = trade_board.get_recent_leads()
                if leads:
                    # Prefer region-local leads if available
                    my_region = getattr(self, 'current_region', None)
                    local = [L for L in leads if my_region and L.get('region') == my_region]
                    last = (local[-1] if local else leads[-1])
                    lt = last.get('type')
                    try:
                        if lt is not None:
                            # Use the lead type exclusively for first attempt
                            prefs['preferred_types'] = [lt]
                            self._lead_context = {'type': lt}
                        else:
                            # Interpret hint-only leads
                            hint = (last.get('hint') or '').lower()
                            from data_sources.harvesters import DataType
                            if 'prefer_structured' in hint:
                                prefs['preferred_types'] = [DataType.STRUCTURED_JSON, DataType.XML_DATA]
                                self._lead_context = {'hint': 'prefer_structured'}
                            elif 'prefer_code' in hint:
                                prefs['preferred_types'] = [DataType.CODE]
                                self._lead_context = {'hint': 'prefer_code'}
                    except Exception:
                        pass
            else:
                # No lead used on this attempt
                self._lead_context = None
            # Occasionally surface strategy in feed to make logs interesting
            try:
                if prefs and random.random() < 0.2:
                    from genesis.stream import doom_feed
                    label = ','.join(t.value for t in preferred_types)
                    msg = f"{self.id} seeks {label}"
                    if 'difficulty_preference' in prefs:
                        msg += f" diff={prefs['difficulty_preference']}"
                    if 'min_freshness' in prefs:
                        msg += f" fresh>{prefs['min_freshness']:.2f}"
                    doom_feed.add('strategy', msg, 1, {'organism': self.id})
                    if getattr(self, 'knowledge_base', None) and random.random() < 0.5:
                        doom_feed.add('intellect', f"{self.id} strategy shaped by knowledge", 1, {'organism': self.id})
            except Exception:
                pass
            return data_ecosystem.find_food_for_organism(self.capabilities, prefs)
        elif attempt_number == 1:
            # Try second-best preference or bias by risk
            if self.has_capability(Capability.PATTERN_MATCH):
                if preferred_types and len(preferred_types) > 1:
                    return data_ecosystem.find_food_for_organism(self.capabilities, {'preferred_types': [preferred_types[1]]})
                if getattr(self, '_brain_drives', None) and self._brain_drives.get('risk', 0.0) > 0.7:
                    return data_ecosystem.find_food_for_organism(self.capabilities, {'preferred_types': [DataType.CODE]})
        elif attempt_number == 2:
            # Memory-based foraging - try to remember good food sources
            if self.has_capability(Capability.REMEMBER) and hasattr(self, 'good_food_memories'):
                for memory in self.good_food_memories[-3:]:  # Last 3 good experiences
                    food = data_ecosystem.find_food_for_organism(self.capabilities)
                    if food and food.data_type == memory.get('food_type'):
                        return food
            # fallback to first preference
            if preferred_types:
                drives = getattr(self, '_brain_drives', {}) or {}
                prefs = {'preferred_types': [preferred_types[0]]}
                if drives.get('conserve', 0.0) > 0.6:
                    prefs['difficulty_preference'] = 'low'
                    prefs['min_freshness'] = 0.5
                return data_ecosystem.find_food_for_organism(self.capabilities, prefs)
        else:
            # Desperate exploration
            if getattr(self, '_brain_drives', None) and self._brain_drives.get('risk', 0.0) > 0.6:
                return data_ecosystem.find_food_for_organism(self.capabilities, {'preferred_types': [DataType.CODE, DataType.XML_DATA]})
            return data_ecosystem.find_food_for_organism(self.capabilities)
        
        return None
    
    def _process_found_food(self, food_morsel, nutrition_system):
        """Process found food with nutritional system AND extract real knowledge"""
        
        # REAL DATA PROCESSING: Extract actual knowledge from internet data
        self._extract_real_knowledge_from_data(food_morsel)
        
        if not nutrition_system:
            # Simple processing
            self.energy += food_morsel.energy_value
            # Reinforcement for simple path
            try:
                if hasattr(self, '_lead_context') and self._lead_context:
                    from data_sources.harvesters import DataType
                    ctx = self._lead_context
                    matched = False
                    if 'type' in ctx and isinstance(ctx['type'], DataType):
                        if food_morsel.data_type == ctx['type']:
                            self.trade_lead_successes += 1
                            matched = True
                    elif 'hint' in ctx:
                        hint = ctx['hint']
                        if hint == 'prefer_structured' and food_morsel.data_type in (DataType.STRUCTURED_JSON, DataType.XML_DATA):
                            self.hint_lead_successes += 1
                            matched = True
                        elif hint == 'prefer_code' and food_morsel.data_type == DataType.CODE:
                            self.hint_lead_successes += 1
                            matched = True
                    if matched:
                        try:
                            from genesis.stream import doom_feed
                            doom_feed.add('lead_success', f"{self.id} validated a shared lead", 1, {'organism': self.id})
                        except Exception:
                            pass
            finally:
                if hasattr(self, '_lead_context'):
                    self._lead_context = None
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

        # Reinforcement: if this success followed a trade/teaching lead, record it and surface
        try:
            if hasattr(self, '_lead_context') and self._lead_context:
                from data_sources.harvesters import DataType
                ctx = self._lead_context
                matched = False
                if 'type' in ctx and isinstance(ctx['type'], DataType):
                    if food_morsel.data_type == ctx['type']:
                        self.trade_lead_successes += 1
                        matched = True
                elif 'hint' in ctx:
                    hint = ctx['hint']
                    if hint == 'prefer_structured' and food_morsel.data_type in (DataType.STRUCTURED_JSON, DataType.XML_DATA):
                        self.hint_lead_successes += 1
                        matched = True
                    elif hint == 'prefer_code' and food_morsel.data_type == DataType.CODE:
                        self.hint_lead_successes += 1
                        matched = True
                if matched:
                    try:
                        from genesis.stream import doom_feed
                        doom_feed.add('lead_success', f"{self.id} validated a shared lead", 1, {'organism': self.id})
                    except Exception:
                        pass
        finally:
            # Clear lead context regardless of match
            if hasattr(self, '_lead_context'):
                self._lead_context = None
        
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

    def _choose_preferred_types(self, n=2, data_ecosystem=None, nutrition_system=None):
        """Choose preferred DataTypes based on brain drives, successes, ecosystem, and metabolic state."""
        try:
            from data_sources.harvesters import DataType
        except Exception:
            return []

        # Base weights
        weights = {
            DataType.SIMPLE_TEXT: 0.1,
            DataType.STRUCTURED_JSON: 0.2,
            DataType.XML_DATA: 0.15,
            DataType.CODE: 0.15,
        }
        # Brain drives
        if getattr(self, '_brain_drives', None):
            ds = self._brain_drives
            weights[DataType.STRUCTURED_JSON] += 0.5 * ds.get('prefer_structured', 0.0)
            weights[DataType.CODE] += 0.5 * (0.5 * ds.get('prefer_structured', 0.0) + ds.get('risk', 0.0))
            weights[DataType.XML_DATA] += 0.2 * ds.get('prefer_structured', 0.0)
        # Memory successes
        if hasattr(self, 'good_food_memories') and self.good_food_memories:
            score = {}
            for m in self.good_food_memories[-10:]:
                t = m.get('food_type')
                score[t] = score.get(t, 0.0) + m.get('energy_gained', 0.0)
            total = sum(score.values()) or 1.0
            for t, s in score.items():
                weights[t] = weights.get(t, 0.0) + 0.3 * (s / total)
        # Knowledge-influenced preferences (proto "intellectual" modulation)
        if getattr(self, 'knowledge_base', None):
            try:
                summary = self.knowledge_base.get_knowledge_summary()
                expertise = [e.lower() for e in summary.get('expertise_areas', [])]
                tech_cues = {'algorithm', 'optimization', 'security', 'database', 'api', 'code'}
                if any(k in expertise for k in tech_cues):
                    weights[DataType.CODE] += 0.3
                trend_cues = {'news', 'trending', 'topic'}
                if any(k in expertise for k in trend_cues):
                    weights[DataType.XML_DATA] += 0.2
                    weights[DataType.STRUCTURED_JSON] += 0.2
            except Exception:
                pass
        # Novelty seeking vs repetition (scaled by novelty_hunger sensor if available)
        drives = getattr(self, '_brain_drives', {}) or {}
        explore_drive = drives.get('explore', 0.0)
        novelty = 0.0
        if hasattr(self, '_last_sensor_map'):
            novelty = max(0.0, min(1.0, self._last_sensor_map.get('novelty_hunger', 0.0)))
        recent_types = []
        if hasattr(self, 'good_food_memories') and self.good_food_memories:
            recent_types = [m.get('food_type') for m in self.good_food_memories[-5:]]
        if explore_drive > 0.7 or novelty > 0.5:
            for dt in [DataType.SIMPLE_TEXT, DataType.STRUCTURED_JSON, DataType.XML_DATA, DataType.CODE]:
                if dt not in recent_types:
                    boost = 0.1 + 0.2 * max(explore_drive - 0.7, 0.0) + 0.2 * max(novelty - 0.5, 0.0)
                    weights[dt] = weights.get(dt, 0.0) + boost
                else:
                    weights[dt] = max(0.0, weights.get(dt, 0.0) - 0.05 * (1.0 + 0.5 * novelty))
        # Ecosystem availability (prefer abundant types)
        if data_ecosystem:
            eco = data_ecosystem.get_ecosystem_stats()
            fbt = eco.get('food_by_type', {})
            total_available = sum(fbt.values()) or 1
            # Competition-aware scaling: under high competition, prefer abundant types more strongly
            comp = 0.0
            if hasattr(self, '_last_sensor_map'):
                comp = max(0.0, min(1.0, float(self._last_sensor_map.get('competition_local', 0.0))))
            avail_scale = 0.25 * (0.6 + 0.8 * comp)  # 0.15..0.45
            for dt in [DataType.SIMPLE_TEXT, DataType.STRUCTURED_JSON, DataType.XML_DATA, DataType.CODE]:
                avail = fbt.get(dt.value, 0) / total_available
                weights[dt] = weights.get(dt, 0.0) + avail_scale * avail
            # Migration intent: if high and scarcity, nudge towards under-consumed types
            scarcity_flag = (eco.get('food_scarcity', 1.0) or 1.0) < 0.4
            if drives.get('migrate', 0.0) > 0.7 and scarcity_flag and recent_types:
                for dt in [DataType.SIMPLE_TEXT, DataType.STRUCTURED_JSON, DataType.XML_DATA, DataType.CODE]:
                    if dt not in recent_types:
                        weights[dt] = weights.get(dt, 0.0) + 0.1
        # Scarcity manager type-specific scarcity (if available)
        if nutrition_system and 'scarcity_manager' in nutrition_system:
            sm = nutrition_system['scarcity_manager']
            for dt in [DataType.SIMPLE_TEXT, DataType.STRUCTURED_JSON, DataType.XML_DATA, DataType.CODE]:
                ts = sm.type_scarcity.get(dt.value, 0.5)
                weights[dt] = weights.get(dt, 0.0) + 0.2 * ts
        # Metabolic adaptability: low efficiency -> prefer simpler/structured; high efficiency -> tolerate more complex
        try:
            me = 0.7
            toxin = 0.0
            if hasattr(self, '_last_sensor_map'):
                me = max(0.0, min(1.0, float(self._last_sensor_map.get('metabolic_efficiency', 0.7))))
                toxin = max(0.0, min(1.0, float(self._last_sensor_map.get('toxicity_buildup', 0.0))))
            if me < 0.4:
                weights[DataType.CODE] *= 0.7
                weights[DataType.SIMPLE_TEXT] = weights.get(DataType.SIMPLE_TEXT, 0.0) + 0.1
                weights[DataType.STRUCTURED_JSON] = weights.get(DataType.STRUCTURED_JSON, 0.0) + 0.1
            elif me > 0.75:
                weights[DataType.CODE] = weights.get(DataType.CODE, 0.0) + 0.12
            # If toxins are high, reduce CODE preference
            if toxin > 0.6:
                weights[DataType.CODE] *= 0.75
        except Exception:
            pass
        # Metabolic recommendations (avoid toxins/addictions)
        if nutrition_system and 'metabolic_tracker' in nutrition_system:
            mt = nutrition_system['metabolic_tracker']
            prof = mt.metabolic_profiles.get(self.id)
            if prof:
                # If toxin buildup is high, reduce preference for complex types (CODE)
                toxin = prof.get('toxin_buildup', 0.0)
                if toxin > 0.5:
                    weights[DataType.CODE] *= 0.7
                # If over-reliant on a type, nudge away
                pf = prof.get('preferred_foods', {})
                if pf:
                    total = sum(pf.values()) or 1
                    most = max(pf, key=pf.get)
                    if pf[most] / total > 0.7:
                        # Reduce that most-eaten type
                        try:
                            from data_sources.harvesters import DataType as DT
                            most_enum = DT(most)
                            weights[most_enum] *= 0.8
                        except Exception:
                            pass
        # Sort by weight
        ordered = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
        return [t for t, _ in ordered[:n] if _ > 0.0]
    
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
            # Doom feed: knowledge pulse
            try:
                from genesis.stream import doom_feed
                doom_feed.add('knowledge', f"{self.id} absorbed {len(knowledge_extracted)} insight(s)", 1,
                              {'organism': self.id})
            except Exception:
                pass
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
                    try:
                        from genesis.stream import doom_feed
                        doom_feed.add('insight', f"{self.id} connected dots: {insight}", 2,
                                      {'organism': self.id})
                    except Exception:
                        pass
                    
                    # Insights make organisms more capable of problem-solving
                    if hasattr(self.traits, 'curiosity'):
                        self.traits.curiosity *= 1.02
            
            # Milestones
            try:
                total = self.knowledge_base.get_knowledge_summary()['total_insights']
                if total >= 1 and 'first_insight' not in self._milestones:
                    self._milestones.add('first_insight')
                    self.known_stories.append('first_insight')
                    from genesis.stream import doom_feed
                    doom_feed.add('milestone', f"{self.id} had a first insight", 2, {'organism': self.id})
                if total >= 10 and 'ten_insights' not in self._milestones:
                    self._milestones.add('ten_insights')
                    self.known_stories.append('ten_insights')
                    from genesis.stream import doom_feed
                    doom_feed.add('milestone', f"{self.id} reached 10 insights", 2, {'organism': self.id})
            except Exception:
                pass
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
                    try:
                        from genesis.stream import doom_feed
                        doom_feed.add('ability', f"{self.id} became a problem-solver", 2, {'organism': self.id})
                    except Exception:
                        pass
                
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

        # BRAIN-INFLUENCED BEHAVIOR MODIFIERS
        if getattr(self, '_brain_drives', None):
            drives = self._brain_drives
            # Initialize container if needed
            if not hasattr(self, '_behavior_modifiers'):
                self._behavior_modifiers = {}
            # Update soft biases from actuators
            self._behavior_modifiers['structure_bias'] = drives.get('prefer_structured', 0.0)
            self._behavior_modifiers['risk_bias'] = drives.get('risk', 0.0)
            self._behavior_modifiers['social_bias'] = drives.get('social', 0.0)
            # Nudge traits slightly based on drives
            if hasattr(self.traits, 'risk_taking'):
                self.traits.risk_taking = min(1.0, max(0.0, self.traits.risk_taking * (1.0 + (drives.get('risk', 0.0) - 0.5) * 0.05)))
            if hasattr(self.traits, 'cooperation'):
                self.traits.cooperation = min(1.0, max(0.0, self.traits.cooperation * (1.0 + (drives.get('social', 0.0) - 0.5) * 0.04)))
            if hasattr(self.traits, 'efficiency'):
                self.traits.efficiency = min(1.0, max(0.0, self.traits.efficiency * (1.0 + (drives.get('conserve', 0.0) - 0.5) * 0.03)))
    
    def communicate_with_other_organisms(self):
        """Simple communication system between organisms"""
        
        # Prepare knowledge summary for chatter (allow communication even without insights)
        knowledge_summary = (self.knowledge_base.get_knowledge_summary()
                             if getattr(self, 'knowledge_base', None)
                             else {'total_insights': 0})
        
        # Brain-derived social drive influences communication likelihood
        social_drive = 0.0
        if getattr(self, '_brain_drives', None):
            social_drive = self._brain_drives.get('social', 0.0)
        
        # Simple signaling based on current state
        social_boost = 0.1 * social_drive
        if self.energy > 80 and random.random() < (0.1 + social_boost):
            # High energy organisms signal success
            print(f"📡 Organism {self.id} signals: Found abundant food source!")
            try:
                from genesis.stream import doom_feed
                doom_feed.add('signal', f"{self.id} boasts of abundance", 1, {'organism': self.id})
            except Exception:
                pass
            
        elif self.energy < 30 and random.random() < (0.15 + social_boost):
            # Low energy organisms signal distress
            print(f"🆘 Organism {self.id} signals: Need help finding food!")
            try:
                from genesis.stream import doom_feed
                doom_feed.add('distress', f"{self.id} calls for help", 3, {'organism': self.id})
            except Exception:
                pass
            
        elif getattr(self, 'knowledge_base', None) and self.knowledge_base.knowledge_items:
            # Sometimes share interesting discoveries
            if random.random() < (0.05 + 0.1 * social_drive):  # stronger with social drive
                recent = self.knowledge_base.knowledge_items[-1]
                if recent.usefulness > 0.6:
                    print(f"💡 Organism {self.id} shares discovery: {recent.content}")
                    try:
                        from genesis.stream import doom_feed
                        doom_feed.add('share', f"{self.id} shares: {recent.content}", 1, {'organism': self.id})
                    except Exception:
                        pass
        
        # React to frustration by calling for help
        if hasattr(self, 'frustration') and self.frustration > 0.8 and random.random() < 0.2:
            print(f"😤 Organism {self.id} signals frustration: Struggling to survive!")
            try:
                from genesis.stream import doom_feed
                doom_feed.add('frustration', f"{self.id} is frustrated", 2, {'organism': self.id})
            except Exception:
                pass
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
            try:
                from genesis.stream import doom_feed
                doom_feed.add('chatter', f"{self.id}: {msg}", 1, {'organism': self.id})
            except Exception:
                pass

        # Teaching inclination influenced by social drive and teach actuator
        if getattr(self, 'knowledge_base', None):
            summary = self.knowledge_base.get_knowledge_summary()
            teach_drive = getattr(self, '_brain_drives', {}).get('teach', 0.0)
            if summary['total_insights'] >= 10 and (social_drive > 0.7 or teach_drive > 0.6) and random.random() < 0.15:
                self._attempt_teaching_action()

        # Trade inclination: share a recent high-yield lead on the trade board
        trade_drive = getattr(self, '_brain_drives', {}).get('trade', 0.0)
        if trade_drive > 0.75 and random.random() < 0.12:
            # Share a good food memory as a lead
            if hasattr(self, 'good_food_memories') and self.good_food_memories:
                best = max(self.good_food_memories[-5:], key=lambda m: m.get('energy_gained', 0.0))
                try:
                    from data_sources.harvesters import DataType
                    ft = best.get('food_type')
                    if isinstance(ft, DataType):
                        trade_board.post_lead(self.id, ft, best.get('source', 'unknown'), best.get('energy_gained', 0.0), region=getattr(self, 'current_region', None))
                    else:
                        # Fallback: just announce
                        from genesis.stream import doom_feed
                        doom_feed.add('trade_offer', f"{self.id} offers lead from {best.get('source','?')}", 1, {'organism': self.id})
                except Exception:
                    pass
            else:
                try:
                    from genesis.stream import doom_feed
                    doom_feed.add('trade_offer', f"{self.id} seeks leads", 1, {'organism': self.id})
                except Exception:
                    pass
        # Migration inclination (placeholder)
        migrate_drive = getattr(self, '_brain_drives', {}).get('migrate', 0.0)
        if migrate_drive > 0.85 and random.random() < 0.05:
            print(f"🚶 Organism {self.id} dreams of migrating to richer habitats")
            try:
                from genesis.stream import doom_feed
                doom_feed.add('migrate_intent', f"{self.id} dreams of migrating", 1, {'organism': self.id})
            except Exception:
                pass

    def _attempt_teaching_action(self):
        print(f"👩‍🏫 Organism {self.id} offers to teach others")
        try:
            from genesis.stream import doom_feed
            doom_feed.add('teach_offer', f"{self.id} offers to teach", 2, {'organism': self.id})
        except Exception:
            pass
        # Self-improvement from teaching attempt
        if hasattr(self, 'organisms_taught'):
            self.organisms_taught.add(self.id + f"_{self.age}")
        if hasattr(self.traits, 'learning_rate'):
            self.traits.learning_rate *= 1.01
        # Share a structural preference hint via trade board to help others
        try:
            drives = getattr(self, '_brain_drives', {}) or {}
            hint = None
            if drives.get('prefer_structured', 0.0) > 0.6:
                hint = 'prefer_structured'
            elif drives.get('risk', 0.0) > 0.7:
                hint = 'prefer_code'
            if hint:
                # Post a hint-only lead (no specific type/source)
                trade_board.post_lead(self.id, None, 'teaching', 0.0, hint=hint, region=getattr(self, 'current_region', None))
        except Exception:
            pass
    
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
        
        # Conserve drive can slightly reduce energy drain
        conserve = 0.0
        if getattr(self, '_brain_drives', None):
            conserve = self._brain_drives.get('conserve', 0.0)
        # Exploration incurs a small activity cost; conservation reduces it
        explore = 0.0
        if getattr(self, '_brain_drives', None):
            explore = self._brain_drives.get('explore', 0.0)
        activity_multiplier = 1.0 + 0.1 * max(0.0, explore - 0.3)  # mild cost when explore is high
        actual_drain = (base_drain * (1.0 - 0.2 * conserve) * activity_multiplier) / efficiency_factor
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
            # Occasionally mutate brain genome as part of organism evolution
            if self.brain_genome and random.random() < 0.05:
                # Snapshot old hidden size to report growth/pruning
                try:
                    old_hid = self.brain_genome.data.get('topology', {}).get('hid', None)
                except Exception:
                    old_hid = None
                self.brain_genome.mutate()
                try:
                    from genesis.brain import Brain
                    self.brain = Brain(self.brain_genome)
                except Exception:
                    pass
                try:
                    from genesis.stream import doom_feed
                    new_hid = self.brain_genome.data.get('topology', {}).get('hid', old_hid)
                    if old_hid is not None and new_hid is not None and new_hid != old_hid:
                        change = 'grew' if new_hid > old_hid else 'pruned'
                        doom_feed.add('evolution', f"{self.id}'s brain {change} hidden layer {old_hid}->{new_hid}", 2,
                                      {'organism': self.id})
                    else:
                        doom_feed.add('evolution', f"{self.id}'s brain rewired itself", 2, {'organism': self.id})
                except Exception:
                    pass
            # Interface shaping based on experience (Task 5):
            # With moderate probability, adapt sensor/actuator gene sets toward useful signals/actions
            if self.brain_genome and random.random() < self._get_interface_adapt_rate():
                try:
                    self._adapt_brain_interfaces_based_on_experience()
                except Exception:
                    pass
        
        # Try to unlock new capability based on experience
        possible_unlocks = self.check_unlock_conditions()
        
        if possible_unlocks:
            new_capability = random.choice(possible_unlocks)
            
            if self.try_unlock(new_capability):
                self.capabilities.add(new_capability)
                print(f"Organism {self.id} unlocked {new_capability.value}!")
                try:
                    from genesis.stream import doom_feed
                    doom_feed.add('unlock', f"{self.id} unlocked {new_capability.value}", 3,
                                  {'organism': self.id, 'capability': new_capability.value})
                except Exception:
                    pass

    def _adapt_brain_interfaces_based_on_experience(self):
        """Evolvable interfaces: grow/prune sensor and actuator genes guided by experience.

        Heuristics (kept simple and safe):
        - If ecosystem/food composition is relevant, ensure availability_* and freshness sensors exist.
        - If metabolism indicates toxins or efficiency shifts, ensure toxicity/metabolic sensors exist.
        - If social/knowledge behaviors are prominent, ensure teach/trade actuators exist.
        - Prune rarely useful sensors when signals are consistently absent.
        """
        if not self.brain_genome or not self.brain:
            return
        from genesis.brain import DEFAULT_SENSORS, DEFAULT_ACTUATORS

        genome = self.brain_genome.data
        sensors = list(genome.get('sensors', list(DEFAULT_SENSORS)))
        actuators = list(genome.get('actuators', list(DEFAULT_ACTUATORS)))

        changed = False

        # Snapshot of last sensed signals if available
        sensor_snapshot = getattr(self, '_last_sensor_map', {}) or {}

        # Prefer including structure/availability and freshness when organism has knowledge
        has_knowledge = (getattr(self, 'knowledge_base', None) is not None and
                         getattr(self.knowledge_base, 'insights_generated', 0) >= 5)
        for useful in ('availability_structured', 'freshness_expectation'):
            if has_knowledge and useful not in sensors and useful in DEFAULT_SENSORS:
                sensors.append(useful)
                changed = True

        # Add metabolic sensors if signals suggest they matter
        if float(sensor_snapshot.get('toxicity_buildup', 0.0)) > 0.4 and 'toxicity_buildup' not in sensors:
            sensors.append('toxicity_buildup'); changed = True
        if 'metabolic_efficiency' in sensor_snapshot and 'metabolic_efficiency' not in sensors:
            sensors.append('metabolic_efficiency'); changed = True

        # If recent success is low, include novelty hunger to encourage exploration
        if float(sensor_snapshot.get('recent_success', 0.5)) < 0.35 and 'novelty_hunger' not in sensors:
            sensors.append('novelty_hunger'); changed = True

        # Prune sensors that are unavailable and likely noise for us
        maybe_prune = []
        for s in ('availability_code', 'availability_structured', 'freshness_expectation', 'toxicity_buildup'):
            val = sensor_snapshot.get(s, None)
            if s in sensors and (val is None or (isinstance(val, (int, float)) and val == 0.0)):
                maybe_prune.append(s)
        # Keep at least a core set; prune at most one per adaptation
        CORE = {'energy', 'frustration', 'memory_load', 'scarcity', 'age', 'capability_density'}
        prunable = [s for s in maybe_prune if s not in CORE]
        if prunable and random.random() < 0.5 and len(sensors) > len(CORE) + 2:
            to_remove = prunable[0]
            sensors.remove(to_remove)
            changed = True

        # Actuators: add teach/trade when behavior/experience supports it
        total_insights = 0
        try:
            if getattr(self, 'knowledge_base', None):
                total_insights = self.knowledge_base.get_knowledge_summary().get('total_insights', 0)
        except Exception:
            pass
        if total_insights >= 10 and 'teach' not in actuators and 'teach' in DEFAULT_ACTUATORS:
            actuators.append('teach'); changed = True
        # If we validated trade/teaching leads, ensure 'trade' actuator present
        if (getattr(self, 'trade_lead_successes', 0) + getattr(self, 'hint_lead_successes', 0)) >= 2 and 'trade' not in actuators:
            actuators.append('trade'); changed = True

        # If competition/scarcity high and migrate not present, consider adding it
        if float(sensor_snapshot.get('competition_local', 0.0)) > 0.7 and 'migrate' not in actuators:
            actuators.append('migrate'); changed = True

        # Guardrails: avoid unbounded growth (bloat)
        MAX_SENSORS = 16
        MAX_ACTUATORS = 12
        if len(sensors) > MAX_SENSORS:
            # prune extras preferring to keep CORE first
            CORE = {'energy', 'frustration', 'memory_load', 'scarcity', 'age', 'capability_density'}
            extras = [s for s in sensors if s not in CORE]
            while len(sensors) > MAX_SENSORS and extras:
                sensors.remove(extras.pop(0))
            changed = True
        if len(actuators) > MAX_ACTUATORS:
            extras_a = [a for a in actuators if a not in ('explore','conserve','social')]
            while len(actuators) > MAX_ACTUATORS and extras_a:
                actuators.remove(extras_a.pop(0))
            changed = True

        if changed:
            # Apply to genome and resize matrices
            old_in = genome.get('topology', {}).get('in', len(self.brain.sensors))
            old_out = genome.get('topology', {}).get('out', len(self.brain.actuators))
            genome['sensors'] = sensors
            genome['actuators'] = actuators
            new_in = len(sensors)
            new_out = len(actuators)
            if new_in != old_in:
                # Safe resize inputs
                try:
                    self.brain_genome._resize_inputs(new_in)
                    genome['topology']['in'] = new_in
                except Exception:
                    pass
            if new_out != old_out:
                try:
                    self.brain_genome._resize_outputs(new_out)
                    genome['topology']['out'] = new_out
                except Exception:
                    pass
            # Rebuild brain phenotype
            try:
                from genesis.brain import Brain
                self.brain = Brain(self.brain_genome)
            except Exception:
                pass
            # Surface event
            try:
                from genesis.stream import doom_feed
                doom_feed.add('interfaces', f"{self.id} adapted brain I/O (in={new_in}, out={new_out})", 1,
                              {'organism': self.id})
            except Exception:
                pass
    
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

            # Region-local interactions (Task 6): teaching and trade
            try:
                if day % 2 == 0:  # light periodicity to limit noise
                    from genesis.interactions import run_region_interactions
                    inter_summary = run_region_interactions(organisms, eco_stats)
                    # Surface a compact summary occasionally
                    if inter_summary and (inter_summary.get('teaching_events', 0) > 0 or inter_summary.get('trade_leads', 0) > 0):
                        from genesis.stream import doom_feed
                        regions = ','.join(f"{r}:{d['population']}" for r, d in inter_summary.get('regions', {}).items())
                        doom_feed.add('interactions', f"teaching={inter_summary.get('teaching_events',0)}, trade={inter_summary.get('trade_leads',0)} [{regions}]", 1)
            except Exception:
                pass
            
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
