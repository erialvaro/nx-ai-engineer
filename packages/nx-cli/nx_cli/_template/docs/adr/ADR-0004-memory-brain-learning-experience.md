# ADR-0004: Project Brain (directory-based), Learning, Experience, Semantic

- **Status:** Accepted
- **Date:** 2026-06-21
- **Sprint:** AIES 3.0 — S2 (PR-5)

## Context
The platform must learn from its own use and remember a project's architecture
across runs — without bloating into a single monolithic file and without ever
storing source code.

## Decision
1. **Project Brain** (`memory/brain.py`) stores knowledge in **specialized
   directories** (architecture, modules, services, apis, database, workflows,
   patterns, history, knowledge, bugs, decisions, retrospectives, adr). Facets
   are key/value JSON; `history`/`retrospectives`/etc. are append-only logs.
   A `looks_like_code` guard drops any code-like value — **knowledge, not code**.
   Versioning bumps on every write; `migrate_legacy()` imports the old
   `memory/architecture.json` non-destructively.
2. **Learning Engine** (`memory/learning.py`) subscribes to
   `run/review/delivery.completed` and writes retrospectives/knowledge/decisions
   into the Brain, emitting `brain.updated`.
3. **Experience** (`experience/metrics.py`) subscribes to the bus and aggregates
   KPIs (success rate, rework/retries, context reduction, …) to
   `.ai-project-assistant/experience/`.
4. **Semantic Knowledge** (`memory/semantic.py`) ships the `SemanticIndex`
   protocol and a dependency-free `NullSemanticIndex` (keyword/Jaccard). A real
   vector index registers later via the SDK with zero caller changes.

## Alternatives considered
- **Single architecture.json.** Rejected by decision #6 (monolith, contention).
- **Store diffs/snippets for learning.** Rejected: the Brain must never hold code.
- **Bundle a vector DB now.** Rejected: breaks zero-dependency; deferred behind
  the Semantic interface.

## Consequences
- Memory now spans `.ai-project-assistant/brain/` and `.ai-project-assistant/experience/`; the legacy
  file still works and is migrated on demand.
- Learning and Experience are pure event subscribers — adding them changed no
  domain engine (Open/Closed).
- Covered by the memory test suite (brain merge/version/code-guard/migration,
  learning handlers, experience KPIs, semantic search).
