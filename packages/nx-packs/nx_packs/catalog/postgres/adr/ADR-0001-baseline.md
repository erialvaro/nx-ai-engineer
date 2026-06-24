# ADR-0001: PostgreSQL baseline

- **Status:** Accepted
- **Domain:** database

## Context
Relational data modeling and PostgreSQL engineering: normalization, relationships, indexing strategy, query performance (EXPLAIN/cost) and safe migrations.

## Decision
Adopt the rules, patterns and anti-patterns in this pack as the engine baseline; run a Database Review before any migration.

## Consequences
Changes are reviewed against `checklists.md`; `anti-patterns.md` violations block delivery.
