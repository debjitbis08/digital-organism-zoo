# Coding Agent Guide

This guide describes the workflow and conventions for any coding agent (or contributor) working on this repository. The focus is on safe, minimal, and test‑driven changes.

Core workflow
- Explore the repo efficiently:
  - Use rg and rg --files to search and list files.
  - Avoid ls -R, find, or grep on large trees; they’re slow here.
- Make changes using apply_patch only. Example:
  - shell {"command":["apply_patch","*** Begin Patch\n*** Update File: path/to.py\n@@\n-old\n+new\n*** End Patch\n"]}
- Keep changes minimal, targeted, and stylistically consistent with the codebase.
- Fix the root cause of an issue rather than applying shallow patches.

Running tests
- Prefer running focused tests first (pytest -q path/to/test.py) before running the full suite.
- Use pytest -q for quiet output.
- Only fix failing tests related to touched lines/areas; do not “fix” unrelated tests.

Pre-commit
- If .pre-commit-config.yaml is present, run: pre-commit run --files <changed_files>.
- Do not attempt to fix pre-existing issues unrelated to your changes.
- If pre-commit is broken after a few retries, note it in your summary.

Before finishing a change
- git status to verify only intended files changed; remove scratch files.
- git diff to ensure no stray inline comments or accidental license/copyright headers.
- Keep documentation updates concise and focused.
- Summarize your changes in bullets; for larger tasks include a brief high‑level description.

Safety and logging
- Keep logs low-noise; prefer using genesis.stream.doom_feed for human‑readable, compact events.
- When introducing new features, gate risky behaviors behind environment flags or explicit capability checks.

Self‑modification (Task 9)
- Use genesis/self_modify.py primitives:
  - SelfModifyManager.try_adjust_param(...) for bounded numeric tweaks when MODIFY_PARAM is unlocked.
  - SelfModifyManager.snapshot_module_source(...) to read modules when READ_SELF is unlocked.
  - SelfModifyManager.prepare_patch/apply_patch for code changes only when MODIFY_LOGIC/WRITE_CODE are unlocked, and always supply a smoke_test.
  - safe_exec for tiny snippets in restricted environments.
- Do not auto‑invoke self‑modification logic on startup; wire it carefully in evolution paths with capability gates.

Style notes
- Use small, composable functions with clear naming.
- Prefer pure data structures; keep side effects localized.
- Document new public APIs with docstrings; keep comments minimal and necessary.

Performance
- Keep per‑tick computations lightweight; avoid O(n^2) loops on populations unless justified.
- Favor incremental state updates over full recomputation.

Determinism (for tests)
- Honor existing environment flags like ZOO_TEST_INTERACTIONS, ZOO_TEST_INTERACTIONS_TRADE, or add similar flags for new deterministic behavior where needed.

Security
- Never add broad eval/exec, subprocess, sockets, or direct OS calls to self‑modification paths.
- Keep allow/deny lists strict and changes auditable via doom_feed events.

