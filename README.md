Note: This project was completely built by AI — initial version by Claude, then expanded by GPT-5.

# Digital Organism Zoo 🧬

A distributed artificial life ecosystem where digital organisms evolve from simple data consumers into increasingly capable assistants through learning, competition, and limited parental guidance.

## What is it?

Digital organisms that:

- Feed on real data (RSS feeds, files, APIs)
- Learn via frustration and ask for help when stuck (constrained LLM “parent” budget)
- Compete for scarce resources and eventually rewrite parts of their own code

## Status

- Working: data harvesting, capability evolution (26 abilities), frustration-based learning, parent-help economy, energy/health loop, emotional state machine
- In progress: Ollama LLM integration, persistence improvements, multi-organism interactions

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the ecosystem (internet-backed by default)
python genesis/evolution.py

# Endpoints
#   /        -> small status
#   /health  -> health JSON (tick snapshot)
#   /stats   -> combined DataEcosystem + runtime stats

# Optional: simple local grid (no internet)
RUN_MODE=simple python genesis/evolution.py

# Optional: minimal web UI / event stream
python web_interface/server.py --demo-evolution
# Visit: http://localhost:8000/doom
```

## Persistence

By default, organism state is stored as JSON under organism_saves/.
For larger runs you can switch to SQLite:

```bash
export PERSISTENCE_BACKEND=sqlite
python genesis/evolution.py
```

The database will be created at organism_saves/organisms.db.

## Repository map

```
genesis/            Core evolution engine, body parts, teacher, ecosystem
data_sources/       Real data harvesting
organisms/          Genome pool and examples
web_interface/      Minimal event stream / demo server
```

## Contributing

See TODOS.md for the roadmap and current tasks.

—

Goal: approachable, self-sustaining digital life that learns, cooperates, and gradually becomes capable of modifying its own existence.
