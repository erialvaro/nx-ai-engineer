# Rules — PostgreSQL

Enforceable rules. The Database Reviewer blocks a change that violates these; the Engineering Contract surfaces them to the agent.

- Never create a duplicate table — always search for an existing entity first.
- Always analyze the relationship and its cardinality before modeling.
- Always validate normalization (1NF→3NF/BCNF); denormalize only with a documented reason.
- Always justify indexes; never create a redundant index.
- Always validate query plans with EXPLAIN ANALYZE and check the cost.
- Every table that needs it keeps its tenant/owner scoping column.
- Foreign keys are explicit; referential integrity is enforced by the database.
- Migrations are reversible; non-null/rename changes ship with a backfill plan.
- Choose the right type — never TEXT/VARCHAR(5000) for bounded values (e.g. a CPF).
