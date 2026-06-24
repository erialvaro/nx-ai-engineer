# Context — PostgreSQL

Model relational data for correctness first, then performance. Reuse existing entities, analyze cardinality and normalization, choose indexes deliberately, and validate every query with EXPLAIN ANALYZE. Never duplicate a table; never add a redundant index. Run a Database Review before any migration.

## Non-negotiables
- Never create a duplicate table — always search for an existing entity first.
- Always analyze the relationship and its cardinality before modeling.
- Always validate normalization (1NF→3NF/BCNF); denormalize only with a documented reason.
- Always justify indexes; never create a redundant index.
- Always validate query plans with EXPLAIN ANALYZE and check the cost.
- Every table that needs it keeps its tenant/owner scoping column.

## Always verify
- 1NF satisfied
- 2NF satisfied
- 3NF satisfied
- BCNF considered
- Primary key defined (and composite PK justified)
- Foreign keys + ON DELETE/UPDATE set
