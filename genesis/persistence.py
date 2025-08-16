# Persistence System for Modified Organisms
# Saves and loads organisms with their code modifications permanently

import json
import pickle
import os
import time
import shutil
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import importlib.util

class OrganismPersistence:
    """Handles saving and loading organisms with code modifications"""
    
    def __init__(self, save_directory="organism_saves"):
        self.save_directory = save_directory
        self.create_save_directory()
        
    def create_save_directory(self):
        """Create save directory structure"""
        os.makedirs(self.save_directory, exist_ok=True)
        os.makedirs(os.path.join(self.save_directory, "organisms"), exist_ok=True)
        os.makedirs(os.path.join(self.save_directory, "code"), exist_ok=True)
        os.makedirs(os.path.join(self.save_directory, "generations"), exist_ok=True)
        
    def save_organism(self, organism) -> str:
        """Save organism with all its modifications permanently"""
        
        organism_id = organism.id
        timestamp = int(time.time())
        
        # Prepare organism data
        organism_data = {
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
            'save_timestamp': timestamp
        }
        
        # Save capabilities
        organism_data['capabilities'] = [cap.value for cap in organism.capabilities]
        
        # Save traits
        traits_data = {}
        for attr in dir(organism.traits):
            if not attr.startswith('_'):
                value = getattr(organism.traits, attr)
                if isinstance(value, (int, float, str, bool)):
                    traits_data[attr] = value
        organism_data['traits'] = traits_data
        
        # Save memory (limited to last 50 items)
        organism_data['memory'] = organism.memory[-50:] if organism.memory else []
        
        # Save code modifications
        if hasattr(organism, 'code_modifications'):
            modifications_data = []
            for mod in organism.code_modifications:
                mod_data = asdict(mod) if hasattr(mod, '__dataclass_fields__') else {
                    'modification_id': getattr(mod, 'modification_id', ''),
                    'modification_type': getattr(mod, 'modification_type', ''),
                    'target_method': getattr(mod, 'target_method', ''),
                    'reason': getattr(mod, 'reason', ''),
                    'created_by': getattr(mod, 'created_by', ''),
                    'timestamp': getattr(mod, 'timestamp', timestamp)
                }
                modifications_data.append(mod_data)
            organism_data['code_modifications'] = modifications_data
        else:
            organism_data['code_modifications'] = []
        
        # Save organism data to JSON
        organism_file = os.path.join(
            self.save_directory, "organisms", 
            f"{organism_id}_{timestamp}.json"
        )
        
        with open(organism_file, 'w') as f:
            json.dump(organism_data, f, indent=2)
        
        # Save code file if it exists
        if hasattr(organism, 'code_file_path') and os.path.exists(organism.code_file_path):
            code_file = os.path.join(
                self.save_directory, "code",
                f"{organism_id}_{timestamp}.py"
            )
            shutil.copy2(organism.code_file_path, code_file)
            organism_data['code_file'] = code_file
            
            # Update JSON with code file reference
            with open(organism_file, 'w') as f:
                json.dump(organism_data, f, indent=2)
        
        print(f"💾 Saved organism {organism_id} (gen {organism.generation}) with {len(organism_data['code_modifications'])} modifications")
        
        return organism_file
        
    def load_organism(self, organism_file: str):
        """Load organism from saved file"""
        
        try:
            with open(organism_file, 'r') as f:
                organism_data = json.load(f)
            
            # Create organism class dynamically if code modifications exist
            if organism_data.get('code_modifications'):
                organism_class = self._create_modified_organism_class(organism_data)
            else:
                # Use base organism class
                from genesis.evolution import Organism
                organism_class = Organism
            
            # Create organism instance
            organism = organism_class(generation=organism_data['generation'])
            
            # Restore basic attributes
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
            
            # Restore capabilities
            from genesis.evolution import Capability
            organism.capabilities = set()
            for cap_name in organism_data.get('capabilities', []):
                try:
                    capability = Capability(cap_name)
                    organism.capabilities.add(capability)
                except ValueError:
                    pass  # Skip invalid capabilities
            
            # Restore traits
            traits_data = organism_data.get('traits', {})
            for attr, value in traits_data.items():
                if hasattr(organism.traits, attr):
                    setattr(organism.traits, attr, value)
            
            # Restore memory
            organism.memory = organism_data.get('memory', [])
            
            # Restore unique food sources
            organism.unique_food_sources = set(organism_data.get('unique_food_sources', []))
            
            print(f"📂 Loaded organism {organism.id} (gen {organism.generation}) with {len(organism_data.get('code_modifications', []))} modifications")
            
            return organism
            
        except Exception as e:
            print(f"❌ Failed to load organism from {organism_file}: {e}")
            return None
    
    def _create_modified_organism_class(self, organism_data):
        """Create organism class with code modifications applied"""
        
        # For now, return base class and apply modifications later
        # In a full implementation, you'd dynamically create the class
        from genesis.evolution import Organism
        return Organism
    
    def save_generation(self, organisms: List, generation_number: int) -> str:
        """Save entire generation of organisms"""
        
        generation_data = {
            'generation_number': generation_number,
            'organism_count': len(organisms),
            'save_timestamp': int(time.time()),
            'organisms': []
        }
        
        # Save each organism and record their files
        for organism in organisms:
            organism_file = self.save_organism(organism)
            generation_data['organisms'].append({
                'organism_id': organism.id,
                'organism_file': organism_file,
                'fitness': getattr(organism, 'current_fitness', 0.0),
                'energy': organism.energy,
                'age': organism.age,
                'modification_count': len(getattr(organism, 'code_modifications', []))
            })
        
        # Save generation summary
        generation_file = os.path.join(
            self.save_directory, "generations",
            f"generation_{generation_number}_{int(time.time())}.json"
        )
        
        with open(generation_file, 'w') as f:
            json.dump(generation_data, f, indent=2)
        
        print(f"📚 Saved generation {generation_number} with {len(organisms)} organisms")
        
        return generation_file
    
    def load_generation(self, generation_file: str) -> List:
        """Load entire generation of organisms"""
        
        try:
            with open(generation_file, 'r') as f:
                generation_data = json.load(f)
            
            organisms = []
            for org_info in generation_data['organisms']:
                organism = self.load_organism(org_info['organism_file'])
                if organism:
                    organisms.append(organism)
            
            print(f"📚 Loaded generation {generation_data['generation_number']} with {len(organisms)} organisms")
            
            return organisms
            
        except Exception as e:
            print(f"❌ Failed to load generation from {generation_file}: {e}")
            return []
    
    def get_save_statistics(self) -> Dict:
        """Get statistics about saved organisms"""
        
        stats = {
            'total_organisms': 0,
            'total_generations': 0,
            'total_modifications': 0,
            'latest_generation': 0,
            'storage_size_mb': 0
        }
        
        # Count organism files
        organism_dir = os.path.join(self.save_directory, "organisms")
        if os.path.exists(organism_dir):
            organism_files = [f for f in os.listdir(organism_dir) if f.endswith('.json')]
            stats['total_organisms'] = len(organism_files)
            
            # Count modifications in organisms
            for org_file in organism_files:
                try:
                    with open(os.path.join(organism_dir, org_file), 'r') as f:
                        data = json.load(f)
                        stats['total_modifications'] += len(data.get('code_modifications', []))
                except:
                    pass
        
        # Count generation files
        generation_dir = os.path.join(self.save_directory, "generations")
        if os.path.exists(generation_dir):
            generation_files = [f for f in os.listdir(generation_dir) if f.endswith('.json')]
            stats['total_generations'] = len(generation_files)
            
            # Find latest generation
            for gen_file in generation_files:
                try:
                    gen_num = int(gen_file.split('_')[1])
                    stats['latest_generation'] = max(stats['latest_generation'], gen_num)
                except:
                    pass
        
        # Calculate storage size
        for root, dirs, files in os.walk(self.save_directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    stats['storage_size_mb'] += os.path.getsize(file_path)
        
        stats['storage_size_mb'] = round(stats['storage_size_mb'] / (1024 * 1024), 2)
        
        return stats
    
    def cleanup_old_saves(self, keep_recent=10):
        """Clean up old organism saves, keeping only recent ones"""
        
        organism_dir = os.path.join(self.save_directory, "organisms")
        if not os.path.exists(organism_dir):
            return
        
        # Get all organism files sorted by timestamp
        organism_files = []
        for f in os.listdir(organism_dir):
            if f.endswith('.json'):
                file_path = os.path.join(organism_dir, f)
                timestamp = os.path.getmtime(file_path)
                organism_files.append((timestamp, file_path, f))
        
        # Sort by timestamp (newest first)
        organism_files.sort(reverse=True)
        
        # Keep only recent files
        files_to_remove = organism_files[keep_recent:]
        
        removed_count = 0
        for timestamp, file_path, filename in files_to_remove:
            try:
                os.remove(file_path)
                
                # Also remove corresponding code file
                code_file = os.path.join(
                    self.save_directory, "code",
                    filename.replace('.json', '.py')
                )
                if os.path.exists(code_file):
                    os.remove(code_file)
                
                removed_count += 1
            except:
                pass
        
        print(f"🧹 Cleaned up {removed_count} old organism saves")

# Integration functions
def create_persistence_system(save_directory="organism_saves"):
    """Create the persistence system"""
    return OrganismPersistence(save_directory)

def auto_save_organisms(organisms: List, persistence_system: OrganismPersistence, generation: int):
    """Automatically save organisms periodically"""
    
    # Save the generation
    persistence_system.save_generation(organisms, generation)
    
    # Cleanup old saves to prevent storage bloat
    if generation % 10 == 0:  # Every 10 generations
        persistence_system.cleanup_old_saves(keep_recent=50)

# Example usage
if __name__ == "__main__":
    print("💾 Testing Persistence System...")
    
    # Create persistence system
    persistence = create_persistence_system("test_saves")
    
    # Show statistics
    stats = persistence.get_save_statistics()
    print(f"Save statistics: {stats}")
    
    print("✅ Persistence system ready!")