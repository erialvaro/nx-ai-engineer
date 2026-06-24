# Rules — MySQL

Enforceable rules. The Database Reviewer blocks a change that violates these; the Engineering Contract surfaces them to the agent.

- Reuse existing entities; never duplicate a table.
- Validate normalization and cardinality.
- Justify every index; avoid redundancy.
- Use InnoDB; foreign keys enforced.
