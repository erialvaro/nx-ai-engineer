# Context — MySQL

Engineering standard for MySQL. Relational modeling on MySQL/InnoDB: normalization, indexing, safe migrations.

## Non-negotiables
- Reuse existing entities; never duplicate a table.
- Validate normalization and cardinality.
- Justify every index; avoid redundancy.
- Use InnoDB; foreign keys enforced.

## Always verify
- 1NF/2NF/3NF
- PK/FK/Unique
- Indexes non-redundant
- EXPLAIN validated
- Migration reversible
