# ADR-0015: Knowledge Engine — coordinating the three project memories

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0013 (Knowledge Providers), ADR-0014 (Obsidian), ADR-0004 (Brain)

## Context
The platform has three distinct memories that were managed in separate places:
the **Project Brain** (operational, current state), **Obsidian** (organizational,
human view) and **Git** (historical record). Nothing owned keeping them
synchronized, and the Context Engine reached into providers/registry directly.

## Decision
Introduce a **Knowledge Engine** (`knowledge/engine.py`) as the single
coordination point and access point, realizing the canonical flow:

```
Project Brain → Knowledge Engine → Knowledge Providers → Obsidian
              → Context Engine → Agents
```

- **Project Brain = operational memory** (canonical current state).
- **Obsidian = organizational memory** (navigable view; reflects the Brain).
- **Git = historical memory** (immutable record).

Responsibilities:
- **Access point**: `retrieve(scope)` / `relationships()` — the Context Engine
  retrieves *through* the Knowledge Engine (it owns the provider registry).
- **Synchronization** (`sync()`): refresh providers → render Obsidian from the
  Brain → optionally snapshot to Git (opt-in `--commit` / `knowledge_git_snapshot`,
  default off). Automatic on `pipeline.completed` / `adr.created`.
- **Status** (`status()`): the alignment of the three memories
  (`synchronized = Obsidian.brain_version == Brain.version`, plus Git head/commits).

The Brain is **injected** (duck-typed), so the knowledge layer still never imports
Memory — no cycle. The Pipeline now builds one Knowledge Engine and shares it
with the Context Engine.

## Alternatives considered
- **Let the Context Engine keep using the registry directly.** Rejected: the flow
  requires a single coordinator; the engine also owns Obsidian sync and the
  three-memory status.
- **Auto-commit to Git on every sync.** Rejected: surprising side effects on the
  user's repo. Git snapshotting is **opt-in**; status always reads Git read-only.
- **Append a sync record to the Brain each sync.** Rejected: it would bump the
  Brain version every sync and defeat Obsidian's incremental writes.

## Consequences
- New CLI: `knowledge sync [--commit]` and `knowledge status` (the three-memory
  view). The Context Engine flows through the Knowledge Engine.
- One place coordinates and reports memory synchronization. Backward compatible
  and additive. Covered by `test_knowledge_engine.py`. Full suite green; no cycles.
