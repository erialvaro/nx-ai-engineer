# Context — Cassandra

Engineering standard for Cassandra. Wide-column modeling on Cassandra: query-first partition/cluster keys.

## Non-negotiables
- Model query-first — one table per query.
- Choose partition keys that spread load.
- Avoid unbounded partitions.
- Never do ad-hoc joins/aggregations.

## Always verify
- One table per query
- Partition key spreads load
- Partition size bounded
- Clustering order set
- No ALLOW FILTERING
