# Rules — Elasticsearch

Enforceable rules. The Database Reviewer blocks a change that violates these; the Engineering Contract surfaces them to the agent.

- Define explicit mappings; avoid dynamic mapping sprawl.
- Model for the search/aggregation patterns.
- Design index lifecycle (ILM) for time-series.
- Bound shard count/size.
