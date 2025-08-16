import asyncio
import sqlite3
import json
from pathlib import Path
from typing import List
import multiprocessing as mp

class DigitalEcosystem:
    """The world where organisms live, eat, and evolve"""
    
    def __init__(self, mode='continue'):
        self.mode = mode
        self.generation = self.load_or_init_generation()
        self.organisms = []
        self.resources = ResourcePool()
        self.teacher = TeacherMind()
        
    def load_or_init_generation(self):
        """Continue evolution or start fresh"""
        state_file = Path('/app/shared_state/generation.json')
        
        if self.mode == 'continue' and state_file.exists():
            with open(state_file) as f:
                state = json.load(f)
                print(f"Continuing from generation {state['generation']}")
                return state['generation']
        else:
            print("Starting genesis - generation 0")
            return 0
    
    def run_forever(self):
        """Main loop - life continues"""
        while True:
            self.tick()
            self.natural_selection()
            self.reproduction_cycle()
            self.save_state()
            
            # Every 100 ticks, evolve
            if self.tick_count % 100 == 0:
                self.generation += 1
                self.evolve_population()
    
    def tick(self):
        """One moment of life"""
        # Run each organism in isolated process
        for organism in self.organisms:
            if organism.energy > 0:
                organism.live()
            else:
                self.organisms.remove(organism)
                self.save_genome(organism)  # Learn from the dead

class ResourcePool:
    """Data sources organisms compete for"""
    
    def __init__(self):
        self.sources = {
            'local_files': {'energy': 5, 'competition': 0},
            'rss_feeds': {'energy': 10, 'competition': 0},
            'system_logs': {'energy': 3, 'competition': 0},
            'user_input': {'energy': 20, 'competition': 0}
        }
    
    def compete_for_resource(self, organisms: List):
        """Only the fast/smart eat"""
        for resource in self.sources:
            competitors = [o for o in organisms if o.wants(resource)]
            if competitors:
                winner = max(competitors, key=lambda o: o.speed * o.intelligence)
                winner.eat(resource)
