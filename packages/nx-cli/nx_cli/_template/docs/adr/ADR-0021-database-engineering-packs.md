# ADR-0021: Database Engineering — Packs (knowledge) × Specialist Agents (execution)

- **Status:** Accepted
- **Date:** 2026-06-23
- **Builds on:** the Engineering Packs (ADR-0019 era) and ADR-0020 (Engineering Contract)

## Context
Database work (relational and NoSQL) carries deep, reusable engineering knowledge —
normalization, indexing, query plans, embedding vs referencing, anti-patterns. If
that knowledge lives "inside a smart agent", it gets duplicated across agents and
cannot be reused or versioned. We want the knowledge to be the asset, not the agent.

## Decision
Model database capability as **two layers**, reusing the existing architecture
(no new mechanism):

1. **Database Engineering Packs** (knowledge) — a `database` category in the pack
   catalog. `postgres` and `mongodb` are authored in full (rules/policies,
   patterns, **anti-patterns**, **performance**, security, checklists, templates,
   examples, an agent **prompt**); mysql, sqlserver, oracle, sqlite, redis,
   cassandra, elastic and neo4j ship as real scaffolds. Packs are **knowledge only**
   (no code, no AI).

2. **Specialist Agents** (execution) — `database-relational`, `database-nosql`,
   and a read-only `database-reviewer`. They **execute** using whatever pack the
   Engineering Contract attaches. The agent is disposable; the pack is not.

A pack `applies_to` several agents, so the **same** PostgreSQL knowledge serves the
Relational, Reviewer (and future Migration/Performance) agents — **no duplication**.
The Engineering Contract auto-attaches packs by `applies_to`.

**Mandatory Database Review.** The `database-reviewer` (read-only) runs before any
migration and **blocks** on: duplicate table/collection, redundant index, missing
FK/integrity, normalization violations, any `anti-patterns.md` hit, or a migration
that is not reversible / not validated by EXPLAIN. Flow:

```
Task → Database Review → Engineering Contract → Agent → Migration → Reviewer → EXPLAIN ANALYZE → Deliver
```

## Consequences
- Knowledge is reusable and versioned in packs; agents stay thin and replaceable.
- Adding an engine or a standard is declarative (author/extend a pack) — no core change.
- The doctrine holds: packs organize knowledge; the model still does all reasoning.
- This is the recommended template for every domain (Security, LGPD, Multi-Tenant,
  Observability, Testing, AI …): a Pack of knowledge + a Specialist Agent that uses it.
