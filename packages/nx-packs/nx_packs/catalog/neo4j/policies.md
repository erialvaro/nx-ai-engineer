# Rules — Neo4j

Enforceable rules. The Database Reviewer blocks a change that violates these; the Engineering Contract surfaces them to the agent.

- Model the domain as nodes + relationships (not tables).
- Index the properties you match on.
- Bound traversal depth; avoid cartesian products.
- Use relationships instead of foreign keys.
