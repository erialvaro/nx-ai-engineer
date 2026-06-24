# Installer Guide

NX AI Engineer installs like any modern developer tool: a package from PyPI and a
single `nxai` CLI. There is **no manual file copying**.

## Install

```bash
pip install nx-ai-engineer
```

This installs the single `nx-ai-engineer` distribution — one wheel that bundles
all 9 `nx_*` modules and the `nxai` console script (the legacy `nx` alias is also
installed). The platform is **stdlib-only** — it pulls in no third-party runtime
dependencies.

Verify:

```bash
nxai version
nxai doctor
```

`nxai doctor` checks the Python version, that every `nx_*` package imports with an
aligned version, that the bundled template is present, whether `git` is on PATH,
and — if you are inside a project — that `.ai-project-assistant/` is valid and writable.

## Initialize a project

From the root of any repository:

```bash
nxai init
```

`init` is idempotent and performs the official bootstrap flow:

1. **Scaffold** `.ai-project-assistant/` — **data only** (the code stays in the installed
   packages). It lays down the deployable template (agent specs, templates,
   project rules, `config.example.json`) and creates the empty data dirs
   (`brain/ knowledge/ obsidian/ tasks/ locks/ reviews/ logs/ memory/`).
2. **Seed** `config.json` from the example (only if you don't already have one).
3. **Audit** — discover and persist the architecture.
4. **Project Brain + Knowledge Engine** — index structured knowledge.
5. **Obsidian Vault** — create the visual vault (folders `00 Dashboard` …
   `14 Retrospectives`).

Options:

- `nxai init <path>` — initialize a project other than the current dir.
- `nxai init --force` — overwrite existing template files (never touches your data).
- `nxai init --no-audit` — scaffold only; run `nxai audit` later.

## What lives where

| Location | Owner | Contents |
|---|---|---|
| site-packages (`nx_*`) | the install | All platform code. Upgraded via `pip`. |
| `.ai-project-assistant/` | your project | **Data only**: config, Project Brain, Obsidian vault, knowledge, tasks, locks, reviews, history. |
| `.ai-project-assistant/agents`, `templates`, `PROJECT_RULES.md` | the template | Refreshed by `nxai update`; safe to customize (your edits to non-template files are never touched). |

## Daily use

```bash
nxai audit                 # (re)discover the architecture
nxai plan "<goal>"         # plan a goal into a task
nxai execute "<goal>"      # full end-to-end flow (dry-run by default, safe)
nxai review                # consolidated diff review
nxai knowledge status      # the three memories (Brain / Obsidian / Git)
nxai docs                  # list the bundled guides
```

Every command is safe by default: execution runs **Dry Run → Test → Execute** and
defaults to dry-run.

## Upgrading

See the [Upgrade Guide](UPGRADE_GUIDE.md): `pip install -U nx-ai-engineer` then
`nxai update` to refresh template assets without touching your Brain/Vault/config.
