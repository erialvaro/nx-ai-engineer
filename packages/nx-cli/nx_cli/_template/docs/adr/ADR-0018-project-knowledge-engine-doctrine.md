# ADR-0018: Project Knowledge Engine doctrine — five responsibilities, no reasoning

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0013 (Providers), ADR-0015 (Engine/3 memories), ADR-0016
  (Project Evolution), ADR-0017 (Graph)

## Context
Across versions the knowledge subsystem grew (providers, three memories, project
evolution, graph). We must keep its scope sharp: AIES is **not** a reasoning
engine. The Project Knowledge Engine must do only knowledge work and never drift
into intelligence — "all intelligence belongs to the AI model".

## Decision
Codify the doctrine as a hard contract:

1. The Knowledge Engine has **exactly five responsibilities**, exposed as named
   methods and listed in `KnowledgeEngine.RESPONSIBILITIES`:
   `discover` · `index` · `relate` · `update` · `deliver_context`.
2. It explicitly does **not** learn programming, improve models, or create
   reasoning. Its only purpose is to **reduce the model's cognitive load**.
3. **Enforcement:** a guardrail test (`test_knowledge_doctrine.py`) parses every
   `aies/knowledge/*.py` and fails the build if it imports any reasoning layer
   (`intelligence`, `schedulers`, `evolution`, `kernel`, `memory`, `governance`,
   `experience`, `observability`, `sdk`, `adapters`). The layer may import only
   `foundation` and `agents` (data/primitives).
4. `deliver_context` returns only structured data (paths/labels) — verified by
   test — so it cannot replace the model's reasoning.
5. `knowledge status` surfaces **context richness** (graph nodes/edges), making
   the principle visible: richer history → richer context → fewer tokens.

The five methods are thin, stable wrappers over existing operations
(`index_all`, `catalog`, `graph`, `sync`, `enrich_context`); no behavior changed.

## Alternatives considered
- **Leave the doctrine as prose only.** Rejected: scope erosion is easy without a
  test. The import guardrail makes the boundary mechanical.
- **Add caching/ranking "intelligence" to the engine.** Rejected: ranking that
  drives decisions belongs to the model/Intelligence layer, not here. The engine
  only surfaces related data.

## Consequences
- The Knowledge Engine's public contract is now explicit and enforced; future
  changes cannot quietly add reasoning to it.
- Backward compatible (additive methods + a doc + a test). New doc
  `PROJECT_KNOWLEDGE.md`. Full suite green; the guardrail test passes (knowledge
  imports only `foundation`/`agents`).
