# ADR-0001: Elasticsearch baseline

- **Status:** Accepted
- **Domain:** database

## Context
Search/document modeling on Elasticsearch: mappings, analyzers, indices.

## Decision
Adopt the rules, patterns and anti-patterns in this pack as the engine baseline; run a Database Review before any migration.

## Consequences
Changes are reviewed against `checklists.md`; `anti-patterns.md` violations block delivery.
