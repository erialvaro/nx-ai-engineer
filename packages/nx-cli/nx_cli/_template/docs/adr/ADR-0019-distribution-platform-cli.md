# ADR-0019: Distribution as a platform — pip + `nxai` CLI + data-only `.ai-project`

- **Status:** Accepted
- **Date:** 2026-06-23
- **Builds on:** the monorepo split (8 acyclic `nx-*` packages) and ADR-0014
  (Obsidian vault), ADR-0018 (Knowledge Engine doctrine)

## Context
The project matured from a copy-based framework (a `framework/` template copied
into `<project>/.ai-project/`, run via `python .ai-project/tools/orchestrator.py`)
into a product that must be **installable, versioned and upgradable** like any
modern developer tool. The copy-based model coupled the engine *code* to each
project, made upgrades a manual re-copy, and could not ship via PyPI.

We also need a single, stable, official user interface, and a project layout that
never risks the user's accumulated knowledge during upgrades.

## Decision
1. **Distribute via PyPI.** `pip install nx-ai-engineer` installs the 8 `nx-*`
   packages and the **`nxai`** console script (the legacy `nx` name stays as an
   alias). The platform is stdlib-only, so the install pulls no third-party
   runtime dependencies.
2. **The deployable template is package data.** Agent specs, doc/code templates,
   project rules, the config example and the guides live under
   `nx_cli/_template/` and ship inside the `nx-cli` wheel — so `nxai init`/`update`
   need **no manual file copying**.
3. **`.ai-project/` is data-only.** The engine code lives in the installed
   packages; a project's `.ai-project/` holds only **data**: `config.json`, the
   Project Brain (`brain/`), the Obsidian vault (`obsidian/`), knowledge, and
   working state (`tasks/ locks/ reviews/ logs/ memory/`).
4. **`nxai init`** scaffolds `.ai-project/` (data dirs + template assets + seeded
   config) and runs the official flow: **audit → Project Brain → Knowledge Engine
   → Obsidian Vault**. It is idempotent and never clobbers user data.
5. **`nxai update`** refreshes only the template-derived assets
   (framework/SDK/providers/templates). It **never** touches `config.json`,
   `brain/`, `obsidian/`, `knowledge/` or history.
6. **Official Obsidian vault structure** — the numbered layout `00 Dashboard` …
   `14 Retrospectives`, created at `init` and auto-synced (still a reflection of
   the Brain, never the source of truth; ADR-0014 doctrine preserved).
7. **Versioning & releases.** Semantic Versioning, reset to **1.0.0** for the
   first public release. A tag-driven GitHub Actions workflow guards on the
   Quality Gate, builds all wheels, publishes to PyPI and creates a GitHub Release.

## Consequences
- Upgrading is `pip install -U nx-ai-engineer` then `nxai update` — the code is
  swapped in site-packages; the project's knowledge is never at risk.
- No behavior was removed: all 19 prior CLI commands remain; the new commands
  (`init`, `update`, `doctor`, `docs`, `version`, `execute`) are additive.
- The legacy `scripts/init_aies.py` and `framework/tools/orchestrator.py` shim
  remain as source-checkout entry points and delegate to the same code.
- The acyclic package graph and the Knowledge Engine doctrine are unchanged.
