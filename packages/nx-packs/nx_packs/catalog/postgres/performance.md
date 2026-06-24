# Performance — PostgreSQL

- Index Scan vs Seq Scan — confirm with EXPLAIN; index selective predicates.
- Bitmap Scan — for medium-selectivity multi-condition queries.
- Covering index (INCLUDE) — serve a query from the index (index-only scan).
- GIN — full-text / jsonb / array containment.
- GiST — ranges / geometry / nearest-neighbour.
- BRIN — huge, naturally-ordered tables (time-series).
- Partial index — index only the rows you query (`WHERE active`).
- Expression index — index `lower(email)` for case-insensitive lookups.
- Partitioning — range/list partitions for very large tables.
- VACUUM / ANALYZE — keep statistics fresh; avoid bloat.
- EXPLAIN ANALYZE — always validate the real plan and cost before shipping.
