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
Status: COMPLETED (initial phase; tests pass; hooks for future tuning)

What’s implemented (now):
- Region grouping and competition hinting:
  - Organisms grouped by current_region; per-organism region population and blended competition metric set and consumed by the brain as competition_local.
- Teaching within region:
  - Teachers with sufficient insights (>=5) or strong foraging memory can teach neighbors; boost scales with teach/social drive; light energy cost; doom_feed events emitted.
  - Test-aware determinism via ZOO_TEST_INTERACTIONS to reliably surface events during tests.
- Trade lead sharing within region:
  - Organisms with good_food_memories post their best recent lead to the shared trade_board; hint-only leads supported; doom_feed events emitted.
  - Region-filtered consumption: trade_board.get_recent_leads(limit, region=...) returns region-local leads when available; organism foraging consumes local leads preferentially.
  - Test-aware determinism via ZOO_TEST_INTERACTIONS_TRADE to ensure posting under tests.
- Observability:
  - Interactions scheduled periodically in the evolution loop with compact summaries in doom_feed.
  - Occasional per-region summary events (population, competition) for low-noise visibility.
- Tests: test_task6_interactions.py validates region grouping, at least one teaching event over two ticks, and successful trade posting without errors.

Notes/Future tweaks:
- Further tune energy/social economics and effect sizes as more behaviors/actuators are added.
- Expand competition observability with richer periodic summaries if needed by UI.

### 🔵 Task 7: Social Learning Between Organisms
File: genesis/ecosystem.py (concept), implemented across: genesis/evolution.py, genesis/interactions.py, genesis/persistence.py
Status: PARTIAL (initial scaffolding; low-noise; backwards compatible)

What’s implemented (now):
- 7.1 Social memory scaffolding
  - Organisms maintain bounded social_observations with (neighbor, behavior, outcome, ts); tiny _trust_map per neighbor.
  - Brain gets optional sensors: social_success_recent and social_failure_recent.
- 7.2 Imitation mechanics (lite)
  - Short-horizon imitation bias (_social_bias) toward recently observed successful food types; decays each tick.
  - Bias integrates into _choose_preferred_types; avoids lock-in via TTL/strength decay.
- 7.3 Knowledge/lead diffusion
  - During teaching, teacher shares a faded best foraging memory with a student (bounded, provenance kept).
  - Student records observation and receives a short-lived imitation seed. Small energy costs applied.
- 7.4 Trust and reputation heuristics
  - Trust updated from observed outcome utility (success/energy). Used to scale imitation strength.
- 7.5 Energetics and costs
  - Small energy cost for teaching and learning to maintain survival economics (balanced and bounded).
- 7.6 Persistence
  - File and SQLite backends persist compact slices of social_observations (last 20) and trust_map (top 10); optional fields restored on load.
- 7.7 Observability
  - Doom feed emits imitate and diffuse events at low noise.

Remaining (future work):
- 7.2 Honor actuator/availability constraints in imitation more explicitly; increase pressure to evolve actuator when missing.
- 7.3 Extend diffusion to topic insights with decay/anti-duplication beyond foraging leads.
- 7.4 Incorporate honesty/lead accuracy signals into trust; add region summary metrics (imitation rate, diffusion volume).
- 7.7 Add periodic per-region summaries for social learning.
- 7.8 Deterministic test hooks (ZOO_TEST_SOCIAL_LEARNING) and helpers to inject synthetic observations.
- 7.9 Add unit/integration tests: imitation bias + decay; trust update; diffusion improves foraging; persistence round-trip.

Notes
- Effects are intentionally small and local; integrated with Task 6 scheduling.
- Logs remain low-noise and compact for UI readability.

### 🟡 Task 8: Genetic Recombination During Reproduction
File: genesis/evolution.py
Status: TODO

### ✅ Task 9: Code Self-Modification Framework
File: genesis/self_modify.py
Status: COMPLETED

What’s implemented (now):
- SelfModifyManager with conservative, safety‑aware building blocks:
  - Introspection utilities (snapshot module source and live object summaries)
  - Parameter tweaks: bounded numeric adjustments with audit log and doom_feed events
  - Safe code patching: prepare_patch + apply_patch with deny‑list, size guards, atomic write, module reload, optional smoke‑test, and rollback on failure
- Shadow patching for offspring‑only trials (apply_patch_shadow) with deterministic version IDs and strict safety checks
- safe_exec helper that evaluates small snippets with a very restricted builtins whitelist and captures stdout
- Evolution wiring (no env flags required):
  - READ_SELF enables occasional self‑introspection
  - MODIFY_PARAM enables tiny, bounded self‑tuning (e.g., learning_rate)
  - MODIFY_LOGIC/WRITE_CODE enable proposing a shadow behavior for offspring‑only trials
- Trial manager processes a small trial budget per tick and accepts/rejects children; behavior changes never hot‑patch the parent
- Tests added (test_task9_self_modify.py): param tweaks and logging; safe_exec constraints; safe vs unsafe patches; smoke‑test rollback; organism self‑tuning and introspection

Notes / optional follow‑ups:
- Optional persistence of param/patch logs and tightened module allow‑lists if needed later

### 🔵 Task 10: Environmental Pressures and Simple-Rule Substrate
File: genesis/environment.py
Status: COMPLETED (initial substrate; default runtime uses it; coarse feedback and adapter added; further demos/tests can expand selection-pressure analysis)

Goal
- Let complexity emerge from simple local rules. Keep the Teacher, but limit its role to light environmental modulation and coarse feedback (no prescriptive topics/insights driving behavior). Primary drivers are energy, local resources, minimal memory, and costly signaling. This yields natural selection pressure (including for “larger brains” via memory size) without adding heavy systems.

Minimal rule set (per tick, simple and local)
- Environment: grid of resource patches with stock S that regrows via logistic rule with light noise; eating depletes S; bounds [0,K].
- Organism state: Energy E, position x, integer memory size M≥0, exploration rate ε∈[0,1], honesty h∈[0,1], and a small FIFO memory of (location→last observed return) up to M.
- Actions:
  - Sense locally within radius R; hear nearby abundance signals.
  - Move: explore with prob ε, else exploit best predicted return from memory/nearby cells.
  - Eat: bite b, gain ΔE=min(b,S), reduce S accordingly.
  - Update memory: store (cell→observed return), evict oldest when full.
  - Signal (optional, costly): if ΔE>T, broadcast “abundance” with prob h; pay c_signal; receivers bias movement toward recent signals.
  - Metabolism: pay c_base + c_mem·M per tick (memory is energetically costly).
  - Reproduce/Die: if E≥E_rep, split with small mutations (M mutates ±1, clamp≥0); if E≤0, die.

Heritability and pressure
- M (memory size) is heritable and mutable; bigger M costs more but improves patch revisitation in stable worlds. Selection will favor/penalize M based on environmental stability without explicit “brain growth” logic.

Integration plan (becomes the default; Task 6 proceeds on top)
- Implement a minimal genesis/environment.py hosting the grid, patch dynamics, and per‑tick scheduling hooks.
- Keep the Teacher but constrain it to:
  - light environment modulation (e.g., r/K/noise per region as a function of external data summarized by the Teacher), and
  - coarse evaluative feedback for optional micro-tasks (tiny energy bonuses),
  without emitting topic insight tokens or direct behavioral advice. Organism “knowledge” is just local memory.
- Keep region/migration from Task 5/6 as virtual regions mapping to grid neighborhoods; signals remain local.

Expected logs (low‑noise)
- “Organism X signaled abundance; N neighbors redirected.”
- “Organism Y memory slots: 5 → 6 (mutation); metabolism cost up.”
- “Patch (i,j) depleted; local crowd disperses.”

Acceptance criteria
- Organisms survive primarily by local patch foraging; the LLM Teacher is present but only modulates the environment and provides coarse feedback. No topic insight tokens are used to steer behavior.
- Mixed strategies emerge (explorers vs exploiters), signaling affects movement, and boom‑bust cycles appear in logs.
- Memory size M shows selection pressure: in stable settings M tends to increase; in volatile settings it decreases due to cost.
- Existing tasks/tests continue to pass (adjust or add shims where necessary) and new unit tests cover the simple‑rules substrate.

Current progress
- Implemented genesis/environment.py with:
  - PatchGrid: logistic regrowth with optional noise, bounded in [0, K]
  - SimpleOrganism: energy, memory size M (FIFO), exploration rate (ε), honesty (h)
  - SimpleEnvironment: per-tick movement (explore/exploit), eating, memory update, costly signaling, metabolism (base + M cost), reproduction with ±1 M mutation; doom_feed events for signaling and reproduction; deterministic under seeded RNG
  - Added depletion observability: emits a compact "Patch (i,j) depleted; local crowd disperses." event when cells hit zero
  - Reproduction logs include metabolism note when child M > parent M ("Metabolism cost up.")
  - Region mapping and teacher modulation: define named rectangular regions and per-region overrides for K, r, noise_std; apply_teacher_modulation emits low-noise log; region-aware regrowth is default.
  - Coarse evaluative feedback hook: apply_coarse_feedback allows tiny energy bonuses/penalties without prescriptive advice (low-noise doom_feed summary)
  - Optional adapter SimpleEnvAdapter exposing get_ecosystem_stats() for light reuse where a DataEcosystem-like API is expected
- Default runtime uses the simple-rule environment (no feature flag):
  - genesis/evolution.py main now boots SimpleEnvironment, seeds organisms, steps the grid, and applies periodic coarse “teacher-like” modulation; emits compact summaries.
  - The previous DataEcosystem remains available for tests/utilities, but is not the default runtime path.
- Added tests (test_task10_environment.py):
  - Validates logistic regrowth and bounds
  - Ensures organisms eat, metabolize, and reproduce with ±1 M mutation
  - Confirms signaling redirects neighbors (with low-noise summary)
  - Verifies per-region modulation affects regrowth averages

Remaining for Task 10
- Optional: Wire real Teacher to environment modulation (coarse deltas for K/r/noise per region; no prescriptive advice), beyond the periodic modulation example in evolution.py.
- Add selection-pressure tests/demos for memory size M (stable vs volatile regimes) and low-noise metrics logging (M distribution over time) to showcase emergent dynamics.

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
