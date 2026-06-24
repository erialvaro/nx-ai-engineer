# Context — Elasticsearch

Engineering standard for Elasticsearch. Search/document modeling on Elasticsearch: mappings, analyzers, indices.

## Non-negotiables
- Define explicit mappings; avoid dynamic mapping sprawl.
- Model for the search/aggregation patterns.
- Design index lifecycle (ILM) for time-series.
- Bound shard count/size.

## Always verify
- Explicit mappings
- Shard sizing
- Analyzers chosen
- ILM/rollover
- Pagination strategy
