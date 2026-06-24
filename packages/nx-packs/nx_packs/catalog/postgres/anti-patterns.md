# Anti-patterns — PostgreSQL

Things the Reviewer flags and blocks.

- `SELECT *` in application queries — select explicit columns.
- N+1 queries — batch / join / use `IN`.
- Duplicate table for the same concept — reuse the existing entity.
- `VARCHAR(5000)` / `TEXT` for bounded values (e.g. a CPF) — use a bounded, typed column.
- Missing foreign key — orphan rows and silent corruption.
- Redundant index — overlaps an existing one; slows writes for no read gain.
- Circular joins — re-model the relationship.
- Unnecessary JSON columns — model real columns when the shape is known.
- Heavy triggers — push logic to the application/queue where appropriate.
