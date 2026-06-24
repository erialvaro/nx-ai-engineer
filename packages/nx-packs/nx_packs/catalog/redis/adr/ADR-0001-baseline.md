# ADR-0001: Redis baseline

- **Status:** Accepted
- **Domain:** database

## Context
Key-value/structure modeling on Redis: access patterns, TTL, memory.

## Decision
Adopt the rules, patterns and anti-patterns in this pack as the engine baseline; run a Database Review before any migration.

## Consequences
Changes are reviewed against `checklists.md`; `anti-patterns.md` violations block delivery.
