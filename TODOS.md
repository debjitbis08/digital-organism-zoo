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

### ✅ Task 4: Neuroevolutionary Brain Structures
File: genesis/brain.py
Status: COMPLETED
- [x] Minimal MLP brain with evolvable genome
- [x] Topology mutation (hidden layer resize with safe weight preservation)
- [x] Sensor/actuator genes; topology.in/out reflect gene counts
- [x] Weight/bias perturbations and rebuild on mutation
- [x] Drives produced from actuators and mapped to behaviors (foraging strategies, energy drain, social/teaching inclination)
- [x] Weighted strategy selection combining drives, memory, ecosystem availability, scarcity, metabolic advice, and knowledge expertise

Deferred follow-ups (new tasks):
- Dual-system brain (instinctual vs intellectual) with clean interfaces
- Deeper actuator-to-action coverage (communication/community/teaching intensity)

### ✅ Task 5: Evolvable Interfaces (Sensors & Actuators)
File: genesis/brain.py, genesis/evolution.py, data_sources/
Status: COMPLETED
Recent work:
- Experience-guided interface adaptation: organisms now add/prune sensor and actuator genes based on their lived signals and successes (e.g., add freshness/availability when knowledge grows; add toxicity/metabolic sensors when relevant; add teach/trade actuators when behaviors succeed). See Organism._adapt_brain_interfaces_based_on_experience() in genesis/evolution.py.
- Automatic, safe topology resizing follows interface changes (uses BrainGenome input/output resizers) and rebuilds phenotype; emits a low-noise 'interfaces' event to the doom feed.
- Actuator-to-behavior mapping tightened: trade/teach/migrate/conserve/risk/prefer_structured signals continue to bias foraging and communication and now gain persistence pressure via interface adaptation.
- Migration actuator is now a real in-sim action via lightweight virtual regions; organisms switch regions based on migrate drive and other drives (prefer_structured/risk/conserve). DataEcosystem applies region bias to food scoring.
- Fitness-linked selection pressure: dynamic interface adaptation rate increases when struggling (low foraging success/toxicity high) and decreases when succeeding, stabilizing beneficial interfaces. Guardrails prevent I/O bloat (caps for sensors/actuators with safe pruning).
- Additional sensors exposed: type-specific scarcity sensors (scarcity_structured, scarcity_code) computed from ecosystem composition and added to the default sensor vocabulary.
- Tests added: test_task5_interfaces.py exercises interface adaptation (with assertions) and deterministic migration via a test flag.

Remaining (future work):
- Extend migration to multi-host P2P (Task 12) once network lands.
- Broader multi-organism convergence tests and minor heuristic tuning as the ecosystem expands.

### 🔵 Task 6: Multi-Organism Interactions
File: genesis/interactions.py (lightweight), genesis/evolution.py (sensors/drives integration)
Status: PARTIAL (passes initial tests)

Implemented so far:
- Region grouping and competition hinting: organisms are grouped by current_region; a region population hint is set per organism and consumed by the brain as competition_local sensor (via Organism._compute_brain_drives()).
- Teaching within region: organisms with sufficient insights (>=5) probabilistically teach neighbors; this boosts the student's foraging_success_rate slightly and leaves a memory hint; events are sent to doom_feed.
- Trade lead sharing within region: organisms with good_food_memories post their best recent lead to the shared trade_board; hint-only leads supported; events are sent to doom_feed.
- Test coverage: test_task6_interactions.py validates region grouping, trade posting, and that at least one teaching event occurs in-region.

Remaining to complete Task 6:
- Integrate region interactions into the main evolution loop so they run periodically without tests invoking them directly.
- Make interactions region-aware for trade consumption (e.g., prefer leads from the same region; optionally per-region trade boards or regional filtering when consuming leads).
- Add light energy/social accounting: small energy cost for teaching; social_interactions increment for both parties; optional cooperation/teach actuator influence on probability and effect size.
- Expand competition hint: blend region population with ecosystem scarcity and type availability; surface an optional _region_competition attribute and doom_feed summaries.
- Deterministic hooks for tests: small env flags to force higher teaching probability in CI when needed without affecting production dynamics.

Acceptance criteria to mark Task 6 done:
- Interactions are scheduled in the evolution loop and observable via doom_feed.
- Region-local teaching and trade measurably influence subsequent foraging behavior and success of nearby organisms.
- Unit tests cover: region grouping stats, at least one teaching event over two interaction ticks, at least one lead posted, and consumption preference for local leads.

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
