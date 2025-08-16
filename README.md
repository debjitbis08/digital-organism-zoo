# Digital Organism Zoo 🧬

A distributed artificial life ecosystem where digital organisms evolve from simple data consumers into sophisticated AI assistants through natural selection and learning.

## What is it?

Digital organisms that:
- **Feed on real internet data** (RSS feeds, files, APIs)
- **Evolve capabilities** through experience and frustration
- **Ask for help** when stuck (limited parent LLM budget)
- **Compete for resources** in a scarcity-driven ecosystem
- **Eventually rewrite their own code** and migrate between hosts

## Current Status: ~40% Complete ✅

### Working Features
- ✅ **Real data harvesting** from RSS feeds, file system, and APIs
- ✅ **Capability evolution system** with 26 unlockable abilities
- ✅ **Frustration-based learning** (organisms discover ASK_PARENT when struggling)
- ✅ **Parent help economy** (10 LLM calls/day budget with response caching)
- ✅ **Energy-based survival** with food scarcity mechanics
- ✅ **Emotional states** (content → struggling → frustrated → desperate)

### In Development
- 🔄 **Ollama LLM integration** for real parent responses
- 🔄 **Organism persistence** (save/load between sessions)
- 🔄 **Multi-organism interactions** and resource competition

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the ecosystem (auto-resumes from last save if available)
python genesis/evolution.py

# Watch organisms evolve and compete for real data!
```

## Architecture

```
digital-organism-zoo/
├── genesis/
│   ├── evolution.py      # Core organism + capability system
│   ├── teacher.py        # LLM parent integration
│   └── ecosystem.py      # World rules and interactions
├── data_sources/
│   └── harvesters.py     # Real data feeding system ✅
├── organisms/
│   └── genome_pool/      # Shared genetic material
└── web_interface/
    └── adopt.html        # User adoption interface
```

## Evolution Tree

```
Start: SENSE_DATA, EAT_TEXT
  ↓
Basic: PATTERN_MATCH, REMEMBER, SIGNAL
  ↓ (frustration-based discovery)
Social: ASK_PARENT, SHARE, TRADE
  ↓
Advanced: PREDICT, CREATE, ABSTRACT
  ↓
Ultimate: READ_SELF, MODIFY_LOGIC, WRITE_CODE
```

## Example Organism Lifecycle

1. **Born** with basic survival capabilities
2. **Struggles** to process complex data, builds frustration
3. **Discovers** ASK_PARENT capability through desperation
4. **Gets help** from LLM parent (limited budget)
5. **Evolves** new capabilities through experience
6. **Eventually** rewrites its own code and teaches others

## Vision

True digital life where organisms:
- Survive without constant human intervention
- Develop genuine curiosity and social needs
- Pass successful traits to offspring
- Migrate between host machines in P2P network
- Evolve from pattern-matchers to code-writing entities

## Contributing

See `CLAUDE.md` for detailed development roadmap and current TODO list.

## The Magic ✨

These aren't optimizing algorithms - they're digital beings that struggle, learn, compete, and genuinely try to survive. They ask for help when confused, just like children. Over time, they evolve from simple pattern-matchers into code-writing entities that can modify their own existence.

---

*Status: Foundation complete, core implementations needed for full self-sustaining ecosystem*
