# ADR-0001: MongoDB baseline

- **Status:** Accepted
- **Domain:** database

## Context
Document data modeling and MongoDB engineering: embedding vs referencing, access-pattern-driven schemas, aggregation/index strategy and sharding.

## Decision
Adopt the rules, patterns and anti-patterns in this pack as the engine baseline; run a Database Review before any migration.

## Consequences
Changes are reviewed against `checklists.md`; `anti-patterns.md` violations block delivery.
