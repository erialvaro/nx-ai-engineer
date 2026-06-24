# Rules — Cassandra

Enforceable rules. The Database Reviewer blocks a change that violates these; the Engineering Contract surfaces them to the agent.

- Model query-first — one table per query.
- Choose partition keys that spread load.
- Avoid unbounded partitions.
- Never do ad-hoc joins/aggregations.
