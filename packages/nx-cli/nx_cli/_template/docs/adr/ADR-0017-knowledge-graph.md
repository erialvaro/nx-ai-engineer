# ADR-0017: Knowledge Graph — automatic relationships to enrich agent context

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0015 (Knowledge Engine), ADR-0016 (Project Evolution),
  ADR-0013 (Knowledge Providers)

## Context
The platform recorded structured knowledge per facet (services, APIs, entities,
tests, bugs, decisions, …) but nothing connected those elements into a graph.
We want the Knowledge Engine to **automatically** relate them —
`Service → API → Database → Migration → Test → ADR → Bug → Feature → Sprint →
Documentation → Obsidian` — and use those relationships **only to enrich the
context** delivered to agents, **never** to replace the model's reasoning.

## Decision
Add a **Knowledge Graph** (`knowledge/graph.py`): a typed `KnowledgeGraph` plus a
`KnowledgeGraphBuilder` that infers nodes and edges automatically from structured
knowledge (never by reading code):
- **co-occurrence** — elements touched together in one execution (Project
  Evolution records) form the `service→api→entity→migration` and `test→service/
  api` chain (edges `serves`/`uses`/`migrates`/`covers`/`delivers`);
- **bugs** → the feature that fixed them (`fixed-in`) and the elements they
  affect (`affects`);
- **sprints** group features by date (`in-sprint`);
- **ADR references** and **doc links** from the providers; **docs → Obsidian**
  (`reflected-in`).

The **Knowledge Engine** exposes `graph()` and `enrich_context(paths)`. The
**Context Engine** calls `enrich_context(ctx.files)` and adds the related
elements (APIs/tests/services/docs/ADRs/bugs) to the agent context — **additive,
capped, deterministic**. The graph returns only data (paths/labels); it makes no
decisions and generates no answers, so it cannot replace the model's reasoning.

New CLI: `knowledge graph [--format summary|mermaid|json] [--query <path>]`. The
Obsidian Relationships note also renders the element graph.

## Alternatives considered
- **Derive relationships by parsing code (imports/calls).** Rejected: violates
  "never interpret code". Co-occurrence + path proximity from structured records
  is safe and sufficient.
- **Let the graph rank/select what the agent must do.** Rejected: the prompt is
  explicit — relationships *enrich* context and must **never replace reasoning**.
  The graph only surfaces related elements.
- **Persist the graph.** Rejected for now: it is derived from the Brain and cheap
  to rebuild; the engine caches it per instance and invalidates on sync.

## Consequences
- Agents receive richer, connected context (e.g., editing a service surfaces its
  API, tests, migration and the related bug/feature) without any change to how
  the model reasons.
- Backward compatible and additive (enrichment is a no-op on an empty Brain).
  Covered by `test_knowledge_graph.py`. Full suite green; no import cycles.
