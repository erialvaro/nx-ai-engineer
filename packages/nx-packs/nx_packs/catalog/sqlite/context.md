# Context — SQLite

Engineering standard for SQLite. Relational modeling on SQLite: pragmatic schemas for embedded/edge.

## Non-negotiables
- Reuse entities.
- Validate normalization.
- Index hot queries; keep it simple.

## Always verify
- 1NF/2NF/3NF
- PK/FK
- Indexes
- PRAGMA foreign_keys ON
- Migration reversible
