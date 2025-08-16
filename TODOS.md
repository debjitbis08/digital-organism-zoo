# Digital Organism Zoo - Development TODO

## Project Status: Foundation Complete, Core Implementation Advancing

### Current Completion: ~40%

- ✅ Evolution system with capability unlocks
- ✅ Frustration-based learning (ASK_PARENT discovery)
- ✅ Parent help economy with budget constraints
- ✅ Energy-based survival mechanics
- ✅ Real data sources (RSS, filesystem, simple APIs)
- ✅ Optional SQLite persistence backend (file-based default retained)
- 🟡 Persistence system (schema migration, backups/versioning TBD)
- 🟡 Brain scaffolding (evolvable genome + forward pass integrated)
- ❌ Multi-organism spatial ecosystem (advanced)
- ❌ LLM language-level teaching (intentionally restricted to biological signals)

---

## Phase 1: Core Life Support 🥇

### ✅ Task 1: Implement Real Data Harvesting System
File: data_sources/harvesters.py
Status: COMPLETED

### ✅ Task 2: Add Nutritional Values Per Data Type
File: genesis/nutrition.py
Status: COMPLETED

### ✅ Task 3: Organism Persistence System
File: genesis/persistence.py
Status: COMPLETED
- [x] File JSON backend with schema v1 and migration helpers
- [x] Atomic generation saves (temp + rename) and latest.json pointer
- [x] Backup copies in organism_saves/backups/
- [x] Optional SQLite backend with transactional generation saves
- [x] Retention policy (env PERSIST_KEEP_RECENT) and cleanup for both backends
- [x] DB maintenance (VACUUM)

---

## Phase 2: Ecosystem Dynamics 🥈

### 🟡 Task 4: Neuroevolutionary Brain Structures
File: genesis/brain.py
Status: PARTIAL (minimal MLP genome, mutation, forward(); integrated for drives)
Next: Topology mutation, sensor/actuator genes, richer decision mapping

### 🟡 Task 5: Evolvable Interfaces (Sensors & Actuators)
File: genesis/brain.py
Status: TODO

### 🟡 Task 6: Multi-Organism Interactions
File: genesis/ecosystem.py
Status: TODO

### 🟡 Task 7: Social Learning Between Organisms
File: genesis/ecosystem.py
Status: TODO

### 🟡 Task 8: Genetic Recombination During Reproduction
File: genesis/evolution.py
Status: TODO

### 🟡 Task 9: Code Self-Modification Framework
File: genesis/self_modify.py
Status: TODO

### 🟡 Task 10: Environmental Pressures and Challenges
File: genesis/environment.py
Status: TODO

---

## Phase 3: Advanced Infrastructure 🥉

### 🔵 Task 11: Doom Feed Event Stream (for "doom scrolling" UI)
File: genesis/stream.py, monitoring/
Status: PARTIAL
- [x] Centralized event feed (doom_feed) with importance levels and in-memory buffer
- [x] Instrument key systems to emit interesting human-readable events
- [ ] Add low-noise aggregation (periodic summaries, throttling)
- [ ] Provide a lightweight HTTP endpoint (NDJSON or SSE) to stream events
- [ ] Build a simple web UI to consume the stream ("doom scrolling" page)

### 🔵 Task 12: P2P Network for Organism Migration
File: network/p2p.py
Status: TODO

### 🔵 Task 13: Genome Pool Shared Between Hosts
File: organisms/genome_pool.py
Status: TODO

### 🔵 Task 14: Docker Container Orchestration
Dir: docker/
Status: TODO

### 🔵 Task 15: Web Interface for Adoption and Monitoring
Dir: web_interface/
Status: TODO

---

## Phase 4: Emergent Intelligence 🏆

### 🟣 Task 16: Advanced Capability Unlocks
File: genesis/advanced_capabilities.py
Status: TODO

### 🟣 Task 17: Organism-to-Organism Teaching
File: genesis/peer_teaching.py
Status: TODO

### 🟣 Task 18: Ecosystem Monitoring and Visualization
Dir: monitoring/
Status: TODO

### 🟣 Task 19: Safety Mechanisms for Code Self-Modification
File: genesis/safety.py
Status: TODO

---

## Notes

- The brain is now created for each organism (random genome) and used to compute simple drives (explore/social) that influence foraging attempts and communication likelihood. Brain genomes mutate occasionally during evolution and persist across saves when using either file or SQLite backends.
- You can switch to the SQLite backend by setting PERSISTENCE_BACKEND=sqlite.

### Immediate Next Steps (Follow this order)
1) Brain evolution (Task 4):
   - Topology mutation (vary hidden size), stronger linkage to sensors/actuators
   - Map outputs to more nuanced actions (foraging strategy selection)
2) Evolvable interfaces (Task 5):
   - Encode sensor/actuator genes; allow brain inputs/outputs to grow/shrink
3) Social learning (Task 7):
   - Observable imitation and knowledge transfer beyond parent care
4) Doom Feed stream (Task 11):
   - Add SSE/NDJSON endpoint and minimal UI to scroll events
