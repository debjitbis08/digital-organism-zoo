# Real Data Harvesting System for Digital Organisms
# Provides actual "food" sources instead of mock data

import json
import time
import threading
import requests
import feedparser
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass
from enum import Enum
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xml.etree.ElementTree as ET

class DataType(Enum):
    """Types of data that organisms can consume"""
    SIMPLE_TEXT = "simple_text"      # Plain text, strings
    STRUCTURED_JSON = "structured_json"  # JSON, YAML
    XML_DATA = "xml_data"            # XML, RSS, ATOM
    CODE = "code"                    # Programming code
    REAL_TIME_STREAM = "real_time_stream"  # Continuous data
    BINARY = "binary"                # Images, files (advanced)

@dataclass
class DataMorsel:
    """A piece of data that organisms can eat"""
    data_type: DataType
    content: str
    size: int
    source: str
    timestamp: float
    energy_value: int
    freshness: float = 1.0  # Decreases over time
    difficulty: int = 1     # Processing complexity
    unique_id: str = None
    
    def __post_init__(self):
        if self.unique_id is None:
            self.unique_id = hashlib.md5(
                f"{self.content}{self.timestamp}".encode()
            ).hexdigest()[:8]
    
    def decay_freshness(self, time_passed: float):
        """Food gets stale over time"""
        decay_rate = 0.1  # 10% per hour
        self.freshness = max(0.0, self.freshness - (decay_rate * time_passed / 3600))
        self.energy_value = int(self.energy_value * self.freshness)
    
    def is_consumable_by_capabilities(self, capabilities: set) -> bool:
        """Check if organism has capabilities to digest this data"""
        from genesis.evolution import Capability
        
        if self.data_type == DataType.SIMPLE_TEXT:
            return Capability.EAT_TEXT in capabilities
        elif self.data_type == DataType.STRUCTURED_JSON:
            return Capability.PATTERN_MATCH in capabilities
        elif self.data_type == DataType.CODE:
            return Capability.ABSTRACT in capabilities
        elif self.data_type == DataType.XML_DATA:
            return Capability.PATTERN_MATCH in capabilities
        else:
            return False

class RSSFeedHarvester:
    """Harvests data from RSS feeds"""
    
    def __init__(self, feed_urls: List[str]):
        self.feed_urls = feed_urls
        self.seen_entries = set()
        self.last_check = {}
        
    def harvest(self) -> List[DataMorsel]:
        """Fetch new entries from RSS feeds"""
        morsels = []
        
        for url in self.feed_urls:
            try:
                feed = feedparser.parse(url)
                
                for entry in feed.entries:
                    entry_id = getattr(entry, 'id', entry.link)
                    
                    if entry_id not in self.seen_entries:
                        self.seen_entries.add(entry_id)
                        
                        # Create morsel from RSS entry
                        content = f"Title: {entry.title}\nSummary: {getattr(entry, 'summary', '')}"
                        
                        morsel = DataMorsel(
                            data_type=DataType.XML_DATA,
                            content=content,
                            size=len(content),
                            source=f"RSS:{feed.feed.title}",
                            timestamp=time.time(),
                            energy_value=15,  # RSS feeds are nutritious
                            difficulty=2
                        )
                        morsels.append(morsel)
                        
            except Exception as e:
                print(f"RSS harvest error for {url}: {e}")
                
        return morsels

class FileSystemHarvester(FileSystemEventHandler):
    """Harvests data from file system changes"""
    
    def __init__(self, watch_paths: List[str], *, chunk_size: int = 4096, max_chunks: int = 500):
        super().__init__()
        self.watch_paths = watch_paths
        self.observer = Observer()
        self.harvested_morsels = []
        self.chunk_size = max(512, int(chunk_size))
        self.max_chunks = max(1, int(max_chunks))
        self.file_extensions = {
            '.txt': DataType.SIMPLE_TEXT,
            '.json': DataType.STRUCTURED_JSON,
            '.xml': DataType.XML_DATA,
            '.py': DataType.CODE,
            '.js': DataType.CODE,
            '.md': DataType.SIMPLE_TEXT,
        }
        
    def start_watching(self):
        """Start monitoring file system"""
        for path in self.watch_paths:
            if os.path.exists(path):
                self.observer.schedule(self, path, recursive=True)
        self.observer.start()
        
    def stop_watching(self):
        """Stop monitoring file system"""
        self.observer.stop()
        self.observer.join()
        
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self._process_file(event.src_path, "modified")
            
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self._process_file(event.src_path, "created")
    
    def _process_file(self, file_path: str, event_type: str):
        """Process a file change into a data morsel"""
        try:
            path = Path(file_path)
            extension = path.suffix.lower()
            
            if extension in self.file_extensions:
                # Read file content and chunk into multiple morsels
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                data_type = self.file_extensions[extension]
                
                # Calculate energy value based on type and size
                base_energy = {
                    DataType.SIMPLE_TEXT: 5,
                    DataType.STRUCTURED_JSON: 12,
                    DataType.XML_DATA: 10,
                    DataType.CODE: 25
                }.get(data_type, 5)
                # Chunking
                chunks = []
                total_len = len(content)
                if total_len == 0:
                    return
                # Limit number of chunks to avoid explosion
                max_chunks = max(1, self.max_chunks)
                step = max(self.chunk_size, 1)
                i = 0
                while i < total_len and len(chunks) < max_chunks:
                    piece = content[i:i+step]
                    i += step
                    # Scale energy with chunk size (sublinear)
                    size = len(piece)
                    energy = int(max(1, base_energy * (1.0 + min(5.0, size / 2000.0))))
                    morsel = DataMorsel(
                        data_type=data_type,
                        content=piece,
                        size=size,
                        source=f"File:{path.name}",
                        timestamp=time.time(),
                        energy_value=energy,
                        difficulty=2 if data_type == DataType.CODE else 1
                    )
                    chunks.append(morsel)
                self.harvested_morsels.extend(chunks)
                print(f"📁 Harvested {len(chunks)} chunk(s) of {data_type.value} from {path.name} ({event_type})")
                
        except Exception as e:
            print(f"File processing error for {file_path}: {e}")
    
    def get_harvested_morsels(self) -> List[DataMorsel]:
        """Get and clear harvested morsels"""
        morsels = self.harvested_morsels.copy()
        self.harvested_morsels.clear()
        return morsels

class APIHarvester:
    """Harvests data from simple APIs"""
    
    def __init__(self):
        self.api_endpoints = [
            {
                'url': 'https://api.github.com/events',
                'name': 'GitHub Events',
                'energy': 20,
                'type': DataType.STRUCTURED_JSON
            },
            {
                'url': 'https://httpbin.org/json',
                'name': 'HTTPBin Test',
                'energy': 10,
                'type': DataType.STRUCTURED_JSON
            },
            # Add more APIs as needed
        ]
        self.request_timeout = 5
        self.last_requests = {}
        self.min_interval = 300  # seconds per endpoint; lowered in aggressive mode via config
        
    def harvest(self) -> List[DataMorsel]:
        """Fetch data from APIs"""
        morsels = []
        
        for endpoint in self.api_endpoints:
            # Rate limiting
            if endpoint['url'] in self.last_requests:
                if time.time() - self.last_requests[endpoint['url']] < self.min_interval:
                    continue
                    
            try:
                response = requests.get(
                    endpoint['url'], 
                    timeout=self.request_timeout,
                    headers={'User-Agent': 'DigitalOrganismZoo/1.0'}
                )
                
                if response.status_code == 200:
                    content = response.text
                    
                    morsel = DataMorsel(
                        data_type=endpoint['type'],
                        content=content,
                        size=len(content),
                        source=f"API:{endpoint['name']}",
                        timestamp=time.time(),
                        energy_value=endpoint['energy'],
                        difficulty=2
                    )
                    
                    morsels.append(morsel)
                    self.last_requests[endpoint['url']] = time.time()
                    print(f"🌐 Harvested from {endpoint['name']}")
                    
            except Exception as e:
                print(f"API harvest error for {endpoint['url']}: {e}")
                
        return morsels

class DataEcosystem:
    """Manages all data sources and provides unified feeding interface"""
    
    def __init__(self, config: Dict[str, Any] = None):
        default_config = self._default_config()
        if config:
            default_config.update(config)
        self.config = default_config
        
        # Initialize harvesters
        self.rss_harvester = RSSFeedHarvester(self.config['rss_feeds'])
        self.file_harvester = FileSystemHarvester(self.config['watch_paths'],
                                                 chunk_size=int(self.config.get('file_chunk_size', 4096)),
                                                 max_chunks=int(self.config.get('file_max_chunks', 500)))
        self.api_harvester = APIHarvester()
        # Allow aggressive API mode
        self.api_harvester.min_interval = int(self.config.get('api_min_interval', 300))

        # Optional synthetic teacher feeder
        self.enable_synthetic_feeder = bool(self.config.get('enable_synthetic_feeder', True))
        
        # Food storage
        self.available_food = []
        self.consumed_food = []
        self.food_scarcity = 1.0  # 1.0 = abundant, 0.0 = scarce

        # Virtual regions: lightweight habitat biases for migration experiments
        # Bias multipliers (>1 favors, <1 disfavors)
        self.region_biases = {
            'default': {
                DataType.SIMPLE_TEXT: 1.0,
                DataType.STRUCTURED_JSON: 1.0,
                DataType.XML_DATA: 1.0,
                DataType.CODE: 1.0,
            },
            'structured-rich': {
                DataType.SIMPLE_TEXT: 1.0,
                DataType.STRUCTURED_JSON: 1.3,
                DataType.XML_DATA: 1.2,
                DataType.CODE: 0.9,
            },
            'code-rich': {
                DataType.SIMPLE_TEXT: 0.8,
                DataType.STRUCTURED_JSON: 1.0,
                DataType.XML_DATA: 0.9,
                DataType.CODE: 1.4,
            },
            'text-meadow': {
                DataType.SIMPLE_TEXT: 1.5,
                DataType.STRUCTURED_JSON: 0.9,
                DataType.XML_DATA: 0.9,
                DataType.CODE: 0.6,
            },
        }
        
        # Start file watching
        self.file_harvester.start_watching()
        
        # Harvesting thread
        self.harvesting = True
        self.harvest_thread = threading.Thread(target=self._harvest_loop, daemon=True)
        self.harvest_thread.start()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for data ecosystem"""
        return {
            'rss_feeds': [
                'https://feeds.bbci.co.uk/news/rss.xml',
                'https://rss.cnn.com/rss/edition.rss',
                'https://hnrss.org/frontpage',  # Hacker News
            ],
            'watch_paths': [
                os.path.expanduser('~/Documents'),
                os.path.expanduser('~/Downloads'),
                '/tmp'  # Temporary files
            ],
            'harvest_interval': 60,  # default to 60s; override at runtime
            'max_food_storage': 1000,
            'scarcity_threshold': 100,
            'enable_synthetic_feeder': True,
            'file_chunk_size': 4096,
            'file_max_chunks': 500,
            'api_min_interval': 120
        }
    
    def _harvest_loop(self):
        """Background harvesting loop"""
        while self.harvesting:
            try:
                # Harvest from all sources
                new_morsels = []
                
                # RSS feeds
                new_morsels.extend(self.rss_harvester.harvest())
                
                # File system
                new_morsels.extend(self.file_harvester.get_harvested_morsels())
                
                # APIs (less frequent)
                if time.time() % 600 < 10:  # Every 10 minutes
                    new_morsels.extend(self.api_harvester.harvest())
                
                # Add to food storage
                self.available_food.extend(new_morsels)
                
                # Manage food storage size
                if len(self.available_food) > self.config['max_food_storage']:
                    # Remove oldest food
                    self.available_food = self.available_food[-self.config['max_food_storage']:]
                
                # Update scarcity
                food_count = len(self.available_food)
                if food_count < self.config['scarcity_threshold']:
                    self.food_scarcity = food_count / self.config['scarcity_threshold']
                else:
                    self.food_scarcity = 1.0
                
                # Decay food freshness
                current_time = time.time()
                for morsel in self.available_food:
                    time_passed = current_time - morsel.timestamp
                    morsel.decay_freshness(time_passed)
                
                # Remove completely stale food
                self.available_food = [m for m in self.available_food if m.freshness > 0.1]

                # Synthetic teacher feeder under scarcity
                if self.enable_synthetic_feeder and len(self.available_food) < (self.config['scarcity_threshold'] // 2):
                    deficit = int(self.config.get('scarcity_threshold', 100)) - len(self.available_food)
                    synth = self._generate_synthetic_food(n=min(20, max(5, deficit)))
                    if synth:
                        self.available_food.extend(synth)
                        print(f"🧠 Teacher feeder added {len(synth)} synthetic morsels. Total food: {len(self.available_food)}")
                
                if new_morsels:
                    print(f"🍽️  Harvested {len(new_morsels)} new morsels. "
                          f"Total food: {len(self.available_food)}, "
                          f"Scarcity: {self.food_scarcity:.2f}")
                
            except Exception as e:
                print(f"Harvest loop error: {e}")
            
            time.sleep(self.config['harvest_interval'])
    
    def find_food_for_organism(self, organism_capabilities: set, preferences: Dict = None) -> Optional[DataMorsel]:
        """Find suitable food for an organism based on its capabilities"""
        
        # Filter food by capabilities
        suitable_food = [
            morsel for morsel in self.available_food
            if morsel.is_consumable_by_capabilities(organism_capabilities)
        ]
        
        if not suitable_food:
            return None
        
        # Apply preferences and scarcity
        if preferences:
            # Preferred data types
            if 'preferred_types' in preferences:
                preferred = [m for m in suitable_food if m.data_type in preferences['preferred_types']]
                if preferred:
                    suitable_food = preferred
            # Filter by minimum freshness
            min_fresh = preferences.get('min_freshness')
            if isinstance(min_fresh, (int, float)):
                suitable_food = [m for m in suitable_food if m.freshness >= max(0.0, min(1.0, float(min_fresh)))]
            # Toxicity avoidance (deprioritize code)
            if preferences.get('toxicity_avoid_code'):
                non_code = [m for m in suitable_food if m.data_type != DataType.CODE]
                if non_code:
                    suitable_food = non_code
        
        # Sort by energy value, freshness, and optional preferences (difficulty, region)
        prefs = preferences or {}
        difficulty_pref = prefs.get('difficulty_preference')
        region = prefs.get('region')
        region_bias = self.region_biases.get(region) if region else None

        def score(m: DataMorsel) -> float:
            base = m.energy_value * m.freshness
            if difficulty_pref == 'low':
                # Prefer easier items (difficulty 1 best)
                base *= 1.0 / (1.0 + 0.3 * max(0, m.difficulty - 1))
            elif difficulty_pref == 'high':
                # Prefer challenging items
                base *= 1.0 + 0.3 * max(0, m.difficulty - 1)
            # Region bias multipliers
            if region_bias is not None:
                base *= float(region_bias.get(m.data_type, 1.0))
            return base

        suitable_food.sort(key=score, reverse=True)
        
        # Return best food item deterministically if available
        if suitable_food:
            chosen_morsel = suitable_food[0]
            self.available_food.remove(chosen_morsel)
            self.consumed_food.append(chosen_morsel)
            return chosen_morsel
        
        return None
    
    def get_ecosystem_stats(self) -> Dict[str, Any]:
        """Get statistics about the data ecosystem"""
        stats = {
            'total_food_available': len(self.available_food),
            'total_food_consumed': len(self.consumed_food),
            'food_scarcity': self.food_scarcity,
            'food_by_type': {},
            'average_freshness': 0.0,
            'total_energy_available': 0
        }
        
        # Calculate food distribution
        for morsel in self.available_food:
            data_type = morsel.data_type.value
            if data_type not in stats['food_by_type']:
                stats['food_by_type'][data_type] = 0
            stats['food_by_type'][data_type] += 1
            stats['total_energy_available'] += morsel.energy_value
        
        # Calculate average freshness
        if self.available_food:
            stats['average_freshness'] = sum(m.freshness for m in self.available_food) / len(self.available_food)
        
        return stats
    
    def stop(self):
        """Stop the data ecosystem"""
        self.harvesting = False
        self.file_harvester.stop_watching()
        if self.harvest_thread.is_alive():
            self.harvest_thread.join(timeout=5)

    # ----------------- Synthetic feeder -----------------
    def _generate_synthetic_food(self, n: int = 10) -> List[DataMorsel]:
        """Generate simple, diverse facts as emergency food.

        Keeps items small and varied to exercise different pathways while
        providing enough quantity for organisms to forage in scarcity.
        """
        n = max(1, int(n))
        facts = [
            "The Earth revolves around the Sun.",
            "Water boils at 100°C at sea level.",
            "Python lists are mutable; tuples are immutable.",
            "JSON stands for JavaScript Object Notation.",
            "XML uses tags to structure data.",
            "APIs allow different software systems to communicate.",
            "Sorting algorithms include quicksort and mergesort.",
            "RSS feeds syndicate updates from websites.",
            "HTTP status 200 means OK.",
            "A byte is 8 bits.",
        ]
        out: List[DataMorsel] = []
        for i in range(n):
            txt = facts[i % len(facts)]
            dt = DataType.SIMPLE_TEXT if i % 3 != 0 else DataType.XML_DATA
            energy = 5 if dt == DataType.SIMPLE_TEXT else 10
            out.append(DataMorsel(
                data_type=dt,
                content=txt,
                size=len(txt),
                source="Teacher:Facts",
                timestamp=time.time(),
                energy_value=energy,
                difficulty=1 if dt == DataType.SIMPLE_TEXT else 2
            ))
        return out

# Example usage and testing
if __name__ == "__main__":
    print("🌱 Starting Digital Organism Data Ecosystem...")
    
    # Create data ecosystem
    ecosystem = DataEcosystem()
    
    try:
        # Simulate organism feeding
        from genesis.evolution import Capability
        
        # Mock organism capabilities
        basic_organism_caps = {Capability.SENSE_DATA, Capability.EAT_TEXT}
        advanced_organism_caps = {Capability.SENSE_DATA, Capability.EAT_TEXT, 
                                Capability.PATTERN_MATCH, Capability.ABSTRACT}
        
        print("\n🤖 Simulating organism feeding...")
        
        for i in range(10):
            time.sleep(5)  # Wait for some data to be harvested
            
            # Try to feed basic organism
            food = ecosystem.find_food_for_organism(basic_organism_caps)
            if food:
                print(f"🍽️  Basic organism ate: {food.data_type.value} "
                      f"({food.energy_value} energy) from {food.source}")
            else:
                print("😋 Basic organism found no suitable food")
            
            # Try to feed advanced organism
            food = ecosystem.find_food_for_organism(advanced_organism_caps)
            if food:
                print(f"🍽️  Advanced organism ate: {food.data_type.value} "
                      f"({food.energy_value} energy) from {food.source}")
            else:
                print("😋 Advanced organism found no suitable food")
            
            # Show ecosystem stats
            stats = ecosystem.get_ecosystem_stats()
            print(f"📊 Ecosystem: {stats['total_food_available']} food available, "
                  f"scarcity: {stats['food_scarcity']:.2f}")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping ecosystem...")
    finally:
        ecosystem.stop()
        print("✅ Data ecosystem stopped")
