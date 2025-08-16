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
import sqlite3

from typing import Dict, List, Optional, Any
from dataclasses import asdict

# Schema version for persistence format
SCHEMA_VERSION = 1

class OrganismPersistence:
    """Handles saving and loading organisms and generations with schema versioning."""

    def __init__(self, save_directory: str = "organism_saves"):
        self.save_directory = save_directory
        self.create_save_directory()
        try:
            self.keep_recent_generations = int(os.getenv('PERSIST_KEEP_RECENT', '50'))
        except Exception:
            self.keep_recent_generations = 50

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
            'social_interactions': getattr(organism, 'social_interactions', 0),
            'failed_attempts': getattr(organism, 'failed_attempts', 0),
            'frustration': getattr(organism, 'frustration', 0.0),
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
            'memory': organism.memory[-50:] if getattr(organism, 'memory', None) else [],
            'code_modifications': []
        }

        if hasattr(organism, 'brain_genome') and organism.brain_genome is not None:
            try:
                organism_data['brain_genome'] = organism.brain_genome.to_dict()
            except Exception:
                pass

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

        organism_file = os.path.join(
            self.save_directory, 'organisms', f"{organism_id}_{timestamp}.json"
        )
        with open(organism_file, 'w') as f:
            json.dump(organism_data, f, indent=2)

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

            ver = organism_data.get('schema_version', 0)
            if ver != SCHEMA_VERSION:
                self._migrate_organism_data(organism_data, ver)

            from genesis.evolution import Organism, Capability
            from genesis.brain import BrainGenome, Brain

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

            if 'brain_genome' in organism_data:
                try:
                    bg = BrainGenome.from_dict(organism_data['brain_genome'])
                    organism.brain_genome = bg
                    organism.brain = Brain(bg)
                except Exception:
                    pass

            print(f"📂 Loaded organism {organism.id} (gen {organism.generation})")
            return organism
        except Exception as e:
            print(f"❌ Failed to load organism: {e}")
            return None

    def save_generation(self, organisms: List, generation_number: int) -> str:
        """Save an entire generation (organisms + summary) with version.)

        Uses temp file + atomic rename and writes a latest.json pointer.
        Also writes a backup copy under organism_saves/backups/.
        """
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

        gen_dir = os.path.join(self.save_directory, 'generations')
        ts = generation_data['save_timestamp']
        gen_name = f"generation_{generation_number}_{ts}.json"
        gen_file = os.path.join(gen_dir, gen_name)
        tmp_file = gen_file + '.tmp'
        with open(tmp_file, 'w') as f:
            json.dump(generation_data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, gen_file)

        # Update latest pointer atomically
        latest_path = os.path.join(gen_dir, 'latest.json')
        latest_tmp = latest_path + '.tmp'
        with open(latest_tmp, 'w') as f:
            json.dump({'generation': generation_number, 'file_path': gen_file, 'timestamp': ts}, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(latest_tmp, latest_path)

        # Backup copy
        backups_dir = os.path.join(self.save_directory, 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        try:
            shutil.copy2(gen_file, os.path.join(backups_dir, gen_name))
        except Exception:
            pass

        print(f"📚 Saved generation {generation_number}")
        return gen_file

    def load_generation(self, generation_file: str) -> List:
        """Load a saved generation, migrate schema, and reconstruct organisms."""
        try:
            with open(generation_file, 'r') as f:
                generation_data = json.load(f)

            ver = generation_data.get('schema_version', 0)
            if ver != SCHEMA_VERSION:
                self._migrate_generation_data(generation_data, ver)
            if 'organisms' not in generation_data or 'generation_number' not in generation_data:
                raise ValueError('Invalid generation file structure')

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

    def cleanup_old_saves(self, keep_recent: Optional[int] = None):
        """Prune old organism saves, keeping only the most recent ones.

        If keep_recent is None, uses configured keep_recent_generations.
        """
        if keep_recent is None:
            keep_recent = self.keep_recent_generations
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
        # Try latest pointer first
        pointer = os.path.join(gen_dir, 'latest.json')
        if os.path.exists(pointer):
            try:
                with open(pointer, 'r') as f:
                    latest = json.load(f)
                    return latest
            except Exception:
                pass
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
        if from_version < 1:
            data.setdefault('memory', [])
            data.setdefault('code_modifications', [])
        data['schema_version'] = SCHEMA_VERSION

    def _migrate_generation_data(self, data: Dict[str, Any], from_version: int):
        """Migrate generation data dict from older schema versions to current."""
        print(f"🛠 Migrating generation data from schema v{from_version} to v{SCHEMA_VERSION}")
        if from_version < 1:
            data.setdefault('organisms', [])
            data.setdefault('save_timestamp', int(time.time()))
        data['schema_version'] = SCHEMA_VERSION
    # END: remove mistakenly inlined file-based methods (moved to OrganismPersistence)

class DBPersistence:
    """SQLite-backed persistence. Stores organisms and generations as JSON blobs.

    This keeps the interface similar to OrganismPersistence while enabling
    faster queries and reduced filesystem churn on large runs.
    """

    def __init__(self, db_path: str = "organism_saves/organisms.db"):
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
        try:
            self.keep_recent_generations = int(os.getenv('PERSIST_KEEP_RECENT', '50'))
        except Exception:
            self.keep_recent_generations = 50

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS organisms (
                    id TEXT,
                    ts INTEGER,
                    generation INTEGER,
                    data TEXT,
                    PRIMARY KEY (id, ts)
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS generations (
                    generation_number INTEGER,
                    ts INTEGER,
                    data TEXT,
                    PRIMARY KEY (generation_number, ts)
                )
                """
            )
            c.execute("CREATE INDEX IF NOT EXISTS idx_gen_ts ON generations(ts)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_org_ts ON organisms(ts)")
            conn.commit()

    # For DB backend, we synthesize a pseudo-path to act as a handle
    @staticmethod
    def _org_handle(org_id: str, ts: int) -> str:
        return f"db://organism/{org_id}/{ts}"

    @staticmethod
    def _gen_handle(gen_number: int, ts: int) -> str:
        return f"db://generation/{gen_number}/{ts}"

    def save_organism(self, organism) -> str:
        timestamp = int(time.time())
        organism_data = {
            'schema_version': SCHEMA_VERSION,
            'id': organism.id,
            'generation': organism.generation,
            'age': organism.age,
            'energy': organism.energy,
            'current_fitness': getattr(organism, 'current_fitness', 0.0),
            'offspring_count': getattr(organism, 'offspring_count', 0),
            'parent_help_received': getattr(organism, 'parent_help_received', 0),
            'social_interactions': getattr(organism, 'social_interactions', 0),
            'failed_attempts': getattr(organism, 'failed_attempts', 0),
            'frustration': getattr(organism, 'frustration', 0.0),
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
            'memory': organism.memory[-50:] if getattr(organism, 'memory', None) else [],
            'code_modifications': []
        }
        # Include brain genome if available
        if hasattr(organism, 'brain_genome') and organism.brain_genome is not None:
            try:
                organism_data['brain_genome'] = organism.brain_genome.to_dict()
            except Exception:
                pass
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO organisms(id, ts, generation, data) VALUES (?, ?, ?, ?)",
                (organism.id, timestamp, organism.generation, json.dumps(organism_data))
            )
            conn.commit()
        handle = self._org_handle(organism.id, timestamp)
        print(f"💾 [DB] Saved organism {organism.id} (gen {organism.generation})")
        return handle

    def _load_organism_by_handle(self, handle: str):
        try:
            parts = handle.split('/')
            org_id, ts = parts[-2], int(parts[-1])
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT data FROM organisms WHERE id=? AND ts=?",
                    (org_id, ts)
                )
                row = c.fetchone()
                if not row:
                    return None
                organism_data = json.loads(row[0])
            ver = organism_data.get('schema_version', 0)
            if ver != SCHEMA_VERSION:
                self._migrate_organism_data(organism_data, ver)
            from genesis.evolution import Organism, Capability
            from genesis.brain import BrainGenome, Brain
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
            # Restore brain
            if 'brain_genome' in organism_data:
                try:
                    bg = BrainGenome.from_dict(organism_data['brain_genome'])
                    organism.brain_genome = bg
                    organism.brain = Brain(bg)
                except Exception:
                    pass
            print(f"📂 [DB] Loaded organism {organism.id} (gen {organism.generation})")
            return organism
        except Exception as e:
            print(f"❌ Failed to load organism from DB: {e}")
            return None

    def load_organism(self, organism_ref: str):
        if organism_ref.startswith('db://'):
            return self._load_organism_by_handle(organism_ref)
        # Fallback to file if a path is provided
        return OrganismPersistence().load_organism(organism_ref)

    def save_generation(self, organisms: List, generation_number: int) -> str:
        # Save organisms and generation in a single transaction
        ts = int(time.time())
        summary = {
            'schema_version': SCHEMA_VERSION,
            'generation_number': generation_number,
            'organism_count': len(organisms),
            'save_timestamp': ts,
            'organisms': []
        }
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            for org in organisms:
                # Build organism JSON (reuse logic from file backend)
                organism_data: Dict[str, Any] = {
                    'schema_version': SCHEMA_VERSION,
                    'id': org.id,
                    'generation': org.generation,
                    'age': org.age,
                    'energy': org.energy,
                    'current_fitness': getattr(org, 'current_fitness', 0.0),
                    'offspring_count': getattr(org, 'offspring_count', 0),
                    'parent_help_received': getattr(org, 'parent_help_received', 0),
                    'social_interactions': getattr(org, 'social_interactions', 0),
                    'failed_attempts': getattr(org, 'failed_attempts', 0),
                    'frustration': getattr(org, 'frustration', 0.0),
                    'unique_food_sources': list(getattr(org, 'unique_food_sources', set())),
                    'energy_efficiency': getattr(org, 'energy_efficiency', 1.0),
                    'known_stories': getattr(org, 'known_stories', []),
                    'cultural_influence': getattr(org, 'cultural_influence', 0.0),
                    'code_version': getattr(org, 'code_version', 1),
                    'last_modified': getattr(org, 'last_modified', ts),
                    'save_timestamp': ts,
                    'capabilities': [cap.value for cap in org.capabilities],
                    'traits': {
                        attr: getattr(org.traits, attr)
                        for attr in dir(org.traits)
                        if not attr.startswith('_') and isinstance(
                            getattr(org.traits, attr), (int, float, str, bool)
                        )
                    },
                    'memory': org.memory[-50:] if getattr(org, 'memory', None) else [],
                    'code_modifications': []
                }
                if hasattr(org, 'brain_genome') and org.brain_genome is not None:
                    try:
                        organism_data['brain_genome'] = org.brain_genome.to_dict()
                    except Exception:
                        pass
                c.execute(
                    "INSERT OR REPLACE INTO organisms(id, ts, generation, data) VALUES (?, ?, ?, ?)",
                    (org.id, ts, org.generation, json.dumps(organism_data))
                )
                summary['organisms'].append({
                    'organism_id': org.id,
                    'organism_file': self._org_handle(org.id, ts),
                    'fitness': getattr(org, 'current_fitness', 0.0),
                    'energy': org.energy,
                    'age': org.age,
                    'modification_count': len(getattr(org, 'code_modifications', []))
                })
            c.execute(
                "INSERT OR REPLACE INTO generations(generation_number, ts, data) VALUES (?, ?, ?)",
                (generation_number, ts, json.dumps(summary))
            )
            conn.commit()
        handle = self._gen_handle(generation_number, ts)
        print(f"📚 [DB] Saved generation {generation_number}")
        return handle

    def cleanup_old_saves(self, keep_recent: Optional[int] = None):
        """Prune old DB generations, keeping only the most recent ones."""
        if keep_recent is None:
            keep_recent = self.keep_recent_generations
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Find timestamps of newest generations to keep
            c.execute("SELECT ts FROM generations ORDER BY ts DESC LIMIT ?", (keep_recent,))
            keep_ts = [row[0] for row in c.fetchall()]
            if keep_ts:
                min_keep = min(keep_ts)
                # Delete generations older than min_keep
                c.execute("DELETE FROM generations WHERE ts < ?", (min_keep,))
                # Delete organisms not referenced by kept timestamps
                c.execute("DELETE FROM organisms WHERE ts < ?", (min_keep,))
                conn.commit()
        print(f"🧹 [DB] Pruned old saves, kept {keep_recent}")

    def vacuum(self):
        """Run SQLite VACUUM to reclaim space after cleanup."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("VACUUM")
            conn.commit()

    def _load_generation_by_handle(self, handle: str) -> List:
        try:
            parts = handle.split('/')
            gen_number, ts = int(parts[-2]), int(parts[-1])
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT data FROM generations WHERE generation_number=? AND ts=?",
                    (gen_number, ts)
                )
                row = c.fetchone()
                if not row:
                    return []
                gen_data = json.loads(row[0])
            ver = gen_data.get('schema_version', 0)
            if ver != SCHEMA_VERSION:
                self._migrate_generation_data(gen_data, ver)
            loaded = []
            for info in gen_data['organisms']:
                org = self.load_organism(info['organism_file'])
                if org:
                    loaded.append(org)
            print(f"📚 [DB] Loaded generation {gen_number} with {len(loaded)} organisms")
            return loaded
        except Exception as e:
            print(f"❌ Failed to load generation from DB: {e}")
            return []

    def load_generation(self, generation_ref: str) -> List:
        if generation_ref.startswith('db://'):
            return self._load_generation_by_handle(generation_ref)
        return OrganismPersistence().load_generation(generation_ref)

    def get_latest_generation_save(self) -> Optional[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT generation_number, ts FROM generations ORDER BY ts DESC LIMIT 1")
                row = c.fetchone()
                if not row:
                    return None
                gen, ts = row
                return {'generation': gen, 'file_path': self._gen_handle(gen, ts), 'timestamp': ts}
        except Exception as e:
            print(f"❌ Failed to fetch latest generation from DB: {e}")
            return None

    # Migration helpers kept consistent with file-based backend
    def _migrate_organism_data(self, data: Dict[str, Any], from_version: int):
        print(f"🛠 Migrating organism data from schema v{from_version} to v{SCHEMA_VERSION}")
        if from_version < 1:
            data.setdefault('memory', [])
            data.setdefault('code_modifications', [])
        data['schema_version'] = SCHEMA_VERSION

    def _migrate_generation_data(self, data: Dict[str, Any], from_version: int):
        print(f"🛠 Migrating generation data from schema v{from_version} to v{SCHEMA_VERSION}")
        if from_version < 1:
            data.setdefault('organisms', [])
            data.setdefault('save_timestamp', int(time.time()))
        data['schema_version'] = SCHEMA_VERSION

def create_persistence_system(save_directory: str = "organism_saves", backend: str = None):
    """Factory for the persistence system.

    backend can be:
    - None or "file" (default): JSON files on disk
    - "sqlite": local SQLite database (organism_saves/organisms.db)

    You can also set PERSISTENCE_BACKEND environment variable to override.
    """
    backend = backend or os.getenv('PERSISTENCE_BACKEND', 'file').lower()
    if backend == 'sqlite':
        return DBPersistence(os.path.join(save_directory, 'organisms.db'))
    return OrganismPersistence(save_directory)

def auto_save_organisms(organisms: List[Any], persistence_system: OrganismPersistence, generation: int):
    """Automatically save organisms and cleanup old saves."""
    persistence_system.save_generation(organisms, generation)
    # Periodically prune according to configured retention policy
    if generation % 10 == 0:
        try:
            persistence_system.cleanup_old_saves(None)
        except TypeError:
            # For backends without optional argument
            persistence_system.cleanup_old_saves()
