# ADR-0001: MySQL baseline

- **Status:** Accepted
- **Domain:** database

## Context
Relational modeling on MySQL/InnoDB: normalization, indexing, safe migrations.

## Decision
Adopt the rules, patterns and anti-patterns in this pack as the engine baseline; run a Database Review before any migration.

## Consequences
Changes are reviewed against `checklists.md`; `anti-patterns.md` violations block delivery.
