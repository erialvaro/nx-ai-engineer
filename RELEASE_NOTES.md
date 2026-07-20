# Release Notes — NX AI Engineer

**NX AI Engineer** is a Developer Infrastructure Platform for AI-assisted
software development. It organizes **knowledge, context and execution** so that
*any* AI model becomes dramatically more effective while building software — it
does not replace Claude Code, GPT, Gemini or any model. **All intelligence
belongs to the model; all organization belongs to NX.**

As of **2.x** it is also a **scaffolding framework**: `nxai new` creates a
complete, Cloud-Agnostic project foundation in one command (FastAPI + Next.js +
Docker Compose + a decoupled Supabase adapter), and `nxai platform-audit` scores
it across eight production dimensions. It ships as a single self-contained wheel
(`pip install nx-ai-engineer`), installable with the `nxai` CLI, with no
third-party runtime dependencies.

## Install

```bash
pip install nx-ai-engineer
nxai version
nxai doctor
```

Then, from any repository:

```bash
nxai init                      # scaffold .ai-project-assistant + audit + Brain + Knowledge + Vault
nxai plan "Add OAuth login"
nxai execute "Add OAuth login" # full flow, Dry Run -> Test -> Execute (dry-run by default)
nxai review
nxai docs                      # the bundled guides
```

## Highlights

- **Free-port preflight (2.8)** — `nxai port [preferred]` finds a bindable
  localhost port **before** a project is brought up on `http://localhost`, so a
  busy port (a stale container, another dev server) never fails startup. `-q`
  prints just the number for scripts (`PORT=$(nxai port 8000 -q)`); scaffolded
  projects also check ports in `make up`. Backed by the stdlib-only
  `nx_core.net` primitive (`is_port_free`, `find_free_port`).
- **Mobile specialist (2.7)** — a `mobile` agent + React Native/Expo Engineering
  Pack: managed Expo + New Architecture, typed navigation, offline-first data,
  secure storage, UI-thread performance, EAS build/update/submit, and mobile a11y.
  Owns RN/Expo files, runs after `frontend`, and receives a matched design
  reference (tokens are platform-agnostic). Prototype with `mockup-app-skill`.
- **Design Reference Library (2.6)** — the `design-references` pack ships visual
  identities distilled from real sites (palette light+dark, type pairing, layout,
  mood, vertical). NX matches the prompt to the best-fit reference by deterministic
  tag overlap and injects it into the `designer`/`frontend` contract, so the AI
  generates sites **grounded in a concrete reference** — *adapt, never clone*.
  Inspect with `nxai design ref list | show <id> | match "<prompt>"`.
- **Official `nxai` CLI** — 26 commands. New in 1.0: `init`, `update`, `doctor`,
  `docs`, `version`, `execute`. The legacy `nx` alias is also installed.
- **PyPI distribution** — 8 acyclic, **stdlib-only** packages (no third-party
  runtime deps). The deployable template ships as package data; **no manual file
  copying**.
- **Data-only `.ai-project-assistant/`** — platform code lives in the installed packages;
  your project keeps only data (config + Project Brain + Obsidian vault +
  knowledge + working state). `nxai update` refreshes template assets and **never**
  touches your Brain/Vault/Knowledge/config/history.
- **Obsidian vault** — the official numbered structure `00 Dashboard` …
  `14 Retrospectives`, created on `init` and auto-synced (a reflection of the
  Brain, never the source of truth).
- **Three memories** — Project Brain (operational, never stores code), Obsidian
  (organizational), Git (historical, opt-in), coordinated by the Knowledge Engine.
- **Knowledge Engine doctrine** — exactly five responsibilities (discover, index,
  relate, update, deliver_context); it never reasons. Enforced by a guardrail test.
- **Open-source ready** — GitHub Actions CI (quality-gate matrix + acyclic graph +
  wheel build), tag-driven PyPI release, issue/PR templates, Installer & Upgrade
  guides.

## Quality bar

Every release must pass the Quality Gate (`python scripts/quality_gate.py`):
**290 tests**, no import cycles, no unused imports, public CLI/API present, all
docs present — plus `scripts/verify_packages.py` (declared **and** real-import
graphs acyclic and consistent).

## Upgrading

```bash
pip install -U nx-ai-engineer
nxai update      # refresh template assets; your data is untouched
```

See the [Upgrade Guide](packages/nx-cli/nx_cli/_template/docs/UPGRADE_GUIDE.md)
and [Installer Guide](packages/nx-cli/nx_cli/_template/docs/INSTALLER_GUIDE.md).
