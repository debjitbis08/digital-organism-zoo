"""
Persistence System for Digital Organisms

This module provides a single OrganismPersistence class responsible for
serializing, saving, loading, and migrating organism and generation data
across simulation runs.
"""
import json
import pickle
import os
import time
import shutil

from typing import Dict, List, Optional, Any
from dataclasses import asdict

# Schema version for persistence format
SCHEMA_VERSION = 1

class OrganismPersistence:
    """Handles saving and loading organisms and generations with schema versioning."""

    def __init__(self, save_directory: str = "organism_saves"):
        self.save_directory = save_directory
        self.create_save_directory()

    def create_save_directory(self):
        """Create directory structure for organism and generation saves."""
        os.makedirs(self.save_directory, exist_ok=True)
        os.makedirs(os.path.join(self.save_directory, "organisms"), exist_ok=True)
        os.makedirs(os.path.join(self.save_directory, "code"), exist_ok=True)
        os.makedirs(os.path.join(self.save_directory, "generations"), exist_ok=True)

    def save_organism(self, organism) -> str:
        """Serialize and save a single organism to JSON (with code files)."""
        organism_id = organism.id
        timestamp = int(time.time())

        organism_data: Dict[str, Any] = {
            'schema_version': SCHEMA_VERSION,
            'id': organism_id,
            'generation': organism.generation,
            'age': organism.age,
            'energy': organism.energy,
            'current_fitness': getattr(organism, 'current_fitness', 0.0),
            'offspring_count': getattr(organism, 'offspring_count', 0),
            'parent_help_received': getattr(organism, 'parent_help_received', 0),
            'social_interactions': organism.social_interactions,
            'failed_attempts': organism.failed_attempts,
            'frustration': organism.frustration,
            'unique_food_sources': list(getattr(organism, 'unique_food_sources', set())),
            'energy_efficiency': getattr(organism, 'energy_efficiency', 1.0),
            'known_stories': getattr(organism, 'known_stories', []),
            'cultural_influence': getattr(organism, 'cultural_influence', 0.0),
            'code_version': getattr(organism, 'code_version', 1),
            'last_modified': getattr(organism, 'last_modified', timestamp),
            'save_timestamp': timestamp,
            'capabilities': [cap.value for cap in organism.capabilities],
            'traits': {
                attr: getattr(organism.traits, attr)
                for attr in dir(organism.traits)
                if not attr.startswith('_') and isinstance(
                    getattr(organism.traits, attr), (int, float, str, bool)
                )
            },
            'memory': organism.memory[-50:] if organism.memory else [],
            'code_modifications': []
        }

        # Serialize code modifications if present
        if hasattr(organism, 'code_modifications'):
            for mod in organism.code_modifications:
                if hasattr(mod, '__dataclass_fields__'):
                    mod_data = asdict(mod)
                    if 'modification_type' in mod_data and hasattr(mod_data['modification_type'], 'value'):
                        mod_data['modification_type'] = mod_data['modification_type'].value
                else:
                    mod_data = {
                        'modification_id': getattr(mod, 'modification_id', ''),
                        'modification_type': getattr(
                            mod, 'modification_type', ''
                        ).value if hasattr(getattr(mod, 'modification_type', ''), 'value') else str(
                            getattr(mod, 'modification_type', '')
                        ),
                        'target_method': getattr(mod, 'target_method', ''),
                        'reason': getattr(mod, 'reason', ''),
                        'created_by': getattr(mod, 'created_by', ''),
                        'timestamp': getattr(mod, 'timestamp', timestamp)
                    }
                organism_data['code_modifications'].append(mod_data)

        # Write organism JSON file
        organism_file = os.path.join(
            self.save_directory, 'organisms', f"{organism_id}_{timestamp}.json"
        )
        with open(organism_file, 'w') as f:
            json.dump(organism_data, f, indent=2)

        # Copy organism code if available
        if hasattr(organism, 'code_file_path') and os.path.exists(organism.code_file_path):
            code_dest = os.path.join(
                self.save_directory, 'code', f"{organism_id}_{timestamp}.py"
            )
            shutil.copy2(organism.code_file_path, code_dest)
            organism_data['code_file'] = code_dest
            with open(organism_file, 'w') as f:
                json.dump(organism_data, f, indent=2)

        print(f"💾 Saved organism {organism_id} (gen {organism.generation})")
        return organism_file

    def load_organism(self, organism_file: str):
        """Load organism JSON, migrate schema, and reconstruct the organism object."""
        try:
            with open(organism_file, 'r') as f:
                organism_data = json.load(f)

            # Migrate schema if needed
            ver = organism_data.get('schema_version', 0)
            if ver != SCHEMA_VERSION:
                self._migrate_organism_data(organism_data, ver)

            from genesis.evolution import Organism, Capability

            organism = Organism(generation=organism_data['generation'])
            organism.id = organism_data['id']
            organism.age = organism_data['age']
            organism.energy = organism_data['energy']
            organism.current_fitness = organism_data.get('current_fitness', 0.0)
            organism.offspring_count = organism_data.get('offspring_count', 0)
            organism.parent_help_received = organism_data.get('parent_help_received', 0)
            organism.social_interactions = organism_data.get('social_interactions', 0)
            organism.failed_attempts = organism_data.get('failed_attempts', 0)
            organism.frustration = organism_data.get('frustration', 0.0)
            organism.energy_efficiency = organism_data.get('energy_efficiency', 1.0)
            organism.known_stories = organism_data.get('known_stories', [])
            organism.cultural_influence = organism_data.get('cultural_influence', 0.0)
            organism.code_version = organism_data.get('code_version', 1)
            organism.last_modified = organism_data.get('last_modified', time.time())

            organism.capabilities = set(
                Capability(cap) for cap in organism_data.get('capabilities', [])
            )

            for attr, val in organism_data.get('traits', {}).items():
                if hasattr(organism.traits, attr):
                    setattr(organism.traits, attr, val)

            organism.memory = organism_data.get('memory', [])
            organism.unique_food_sources = set(
                organism_data.get('unique_food_sources', [])
            )

            print(f"📂 Loaded organism {organism.id} (gen {organism.generation})")
            return organism
        except Exception as e:
            print(f"❌ Failed to load organism: {e}")
            return None

    def save_generation(self, organisms: List, generation_number: int) -> str:
        """Save an entire generation (organisms + summary) with version."""
        generation_data: Dict[str, Any] = {
            'schema_version': SCHEMA_VERSION,
            'generation_number': generation_number,
            'organism_count': len(organisms),
            'save_timestamp': int(time.time()),
            'organisms': []
        }
        for org in organisms:
            org_file = self.save_organism(org)
            generation_data['organisms'].append({
                'organism_id': org.id,
                'organism_file': org_file,
                'fitness': getattr(org, 'current_fitness', 0.0),
                'energy': org.energy,
                'age': org.age,
                'modification_count': len(getattr(org, 'code_modifications', []))
            })

        gen_file = os.path.join(
            self.save_directory, 'generations',
            f"generation_{generation_number}_{int(time.time())}.json"
        )
        with open(gen_file, 'w') as f:
            json.dump(generation_data, f, indent=2)

        print(f"📚 Saved generation {generation_number}")
        return gen_file

    def load_generation(self, generation_file: str) -> List:
        """Load a saved generation, migrate schema, and reconstruct organisms."""
        try:
            with open(generation_file, 'r') as f:
                generation_data = json.load(f)

            # Migrate schema if needed
            ver = generation_data.get('schema_version', 0)
            if ver != SCHEMA_VERSION:
                self._migrate_generation_data(generation_data, ver)

            loaded = []
            for info in generation_data['organisms']:
                org = self.load_organism(info['organism_file'])
                if org:
                    loaded.append(org)

            print(f"📚 Loaded generation {generation_data['generation_number']} with {len(loaded)} organisms")
            return loaded
        except Exception as e:
            print(f"❌ Failed to load generation: {e}")
            return []

    def get_save_statistics(self) -> Dict[str, Any]:
        """Gather stats about stored organisms and generations."""
        stats = {
            'total_organisms': 0,
            'total_generations': 0,
            'latest_generation': 0,
            'storage_mb': 0.0
        }
        org_dir = os.path.join(self.save_directory, 'organisms')
        if os.path.isdir(org_dir):
            files = [f for f in os.listdir(org_dir) if f.endswith('.json')]
            stats['total_organisms'] = len(files)
        gen_dir = os.path.join(self.save_directory, 'generations')
        if os.path.isdir(gen_dir):
            files = [f for f in os.listdir(gen_dir) if f.endswith('.json')]
            stats['total_generations'] = len(files)
            for f in files:
                try:
                    num = int(f.split('_')[1])
                    stats['latest_generation'] = max(stats['latest_generation'], num)
                except:
                    pass
        for root, _, files in os.walk(self.save_directory):
            for f in files:
                fp = os.path.join(root, f)
                stats['storage_mb'] += os.path.getsize(fp)
        stats['storage_mb'] = round(stats['storage_mb'] / (1024*1024), 2)
        return stats

    def cleanup_old_saves(self, keep_recent: int = 10):
        """Prune old organism saves, keeping only the most recent ones."""
        org_dir = os.path.join(self.save_directory, 'organisms')
        if not os.path.isdir(org_dir):
            return
        entries = []
        for f in os.listdir(org_dir):
            if f.endswith('.json'):
                path = os.path.join(org_dir, f)
                entries.append((os.path.getmtime(path), path, f))
        entries.sort(reverse=True)
        for _, path, fname in entries[keep_recent:]:
            os.remove(path)
            code_file = os.path.join(self.save_directory, 'code', fname.replace('.json', '.py'))
            if os.path.exists(code_file):
                os.remove(code_file)
        print(f"🧹 Cleaned up old organism saves, kept {keep_recent}")

    def get_latest_generation_save(self) -> Optional[Dict[str, Any]]:
        """Return metadata for the most recent generation save for resumption."""
        gen_dir = os.path.join(self.save_directory, 'generations')
        if not os.path.isdir(gen_dir):
            return None
        candidates = []
        for f in os.listdir(gen_dir):
            if f.startswith('generation_') and f.endswith('.json'):
                parts = f.split('_')
                try:
                    num = int(parts[1])
                    path = os.path.join(gen_dir, f)
                    ts = os.path.getmtime(path)
                    candidates.append({'generation': num, 'file_path': path, 'timestamp': ts})
                except:
                    continue
        if not candidates:
            return None
        latest = max(candidates, key=lambda x: x['timestamp'])
        print(f"📍 Latest save found: generation {latest['generation']}")
        return latest

    def _migrate_organism_data(self, data: Dict[str, Any], from_version: int):
        """Migrate organism data dict from older schema versions to current."""
        print(f"🛠 Migrating organism data from schema v{from_version} to v{SCHEMA_VERSION}")
        # Migrate legacy organism defaults from version 0
        if from_version < 1:
            data.setdefault('memory', [])
            data.setdefault('code_modifications', [])
        data['schema_version'] = SCHEMA_VERSION

    def _migrate_generation_data(self, data: Dict[str, Any], from_version: int):
        """Migrate generation data dict from older schema versions to current."""
        print(f"🛠 Migrating generation data from schema v{from_version} to v{SCHEMA_VERSION}")
        # Migrate legacy generation defaults from version 0
        if from_version < 1:
            data.setdefault('organisms', [])
            data.setdefault('save_timestamp', int(time.time()))
        data['schema_version'] = SCHEMA_VERSION

def create_persistence_system(save_directory: str = "organism_saves") -> OrganismPersistence:
    """Convenience factory for the persistence system."""
    return OrganismPersistence(save_directory)

def auto_save_organisms(organisms: List[Any], persistence_system: OrganismPersistence, generation: int):
    """Automatically save organisms and cleanup old saves."""
    persistence_system.save_generation(organisms, generation)
    if generation % 10 == 0:
        persistence_system.cleanup_old_saves(keep_recent=50)
