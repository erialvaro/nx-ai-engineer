# ADR-0001: Oracle baseline

- **Status:** Accepted
- **Domain:** database

## Context
Relational modeling on Oracle: partitioning, indexing, cost-based plans.

## Decision
Adopt the rules, patterns and anti-patterns in this pack as the engine baseline; run a Database Review before any migration.

## Consequences
Changes are reviewed against `checklists.md`; `anti-patterns.md` violations block delivery.
