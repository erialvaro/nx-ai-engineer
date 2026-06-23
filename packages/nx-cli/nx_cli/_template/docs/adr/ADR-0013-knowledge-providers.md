# ADR-0013: Knowledge Providers — decouple knowledge sources from the Context Engine

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0003 (Context Engine), ADR-0004 (Brain/Semantic)

## Context
The Context Engine read knowledge sources directly: it walked the filesystem
(`os.walk`) inside `ContextBuilder.build`, and its resolvers were the only way to
bring knowledge in. Adding a new source (git, markdown structure, ADRs, the
Project Brain, an Obsidian vault) meant editing the Context Engine. Knowledge
acquisition and context assembly were entangled.

## Decision
Introduce a **Knowledge Provider** architecture (`aies/knowledge/`). No knowledge
source is coupled directly to the Context Engine; every source is a
`KnowledgeProvider` that only **indexes / catalogs / retrieves / enriches /
relates** — and **never decides, interprets code, or generates answers**.

Built-in providers: **Filesystem, Git, Markdown, ADR, Project-Brain, Obsidian**.
A `KnowledgeRegistry` is the single entry point; new providers register without
touching the Context Engine.

The **Context Engine** now:
- gets its file list and version from the **Filesystem Provider** (no `os.walk`);
- enriches docs from the **Markdown + ADR** providers and patterns from the
  **Project-Brain** provider, via the registry.

### Acyclicity
The knowledge layer **does not import Memory**. The Project-Brain provider
receives the Brain by injection (duck-typed), so the dependency direction stays
`Memory → Knowledge` only — verified: no import cycles.

## Alternatives considered
- **Keep resolvers reading the FS directly.** Rejected: that is exactly the
  coupling this ADR removes; new sources would keep editing the Context Engine.
- **Make providers rank/decide relevance.** Rejected: providers *provide*;
  ranking/relevance and agent decisions belong to the Context Engine and the
  Intelligence layer. Providers do only presence-based retrieval ordering.
- **Have the Brain provider import the Brain class.** Rejected: would create a
  Memory↔Knowledge cycle. Injection keeps it acyclic.

## Consequences
- New CLI: `knowledge index|list|retrieve [--provider] [--query] [--limit]`.
- Knowledge sources are pluggable and testable in isolation; the Context Engine
  is independent of where knowledge comes from.
- Backward compatible: `ContextBuilder` API and outputs unchanged (the file list
  now flows through a provider; docs/patterns are additively enriched).
- Covered by `test_knowledge.py` (base contract, all 6 providers, registry,
  context wiring). Full suite green; no import cycles (quality gate enforces).
