# ADR-0001: SQL Server baseline

- **Status:** Accepted
- **Domain:** database

## Context
Relational modeling on SQL Server: indexing, execution plans, migrations.

## Decision
Adopt the rules, patterns and anti-patterns in this pack as the engine baseline; run a Database Review before any migration.

## Consequences
Changes are reviewed against `checklists.md`; `anti-patterns.md` violations block delivery.
