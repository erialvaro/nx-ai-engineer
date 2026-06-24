# Anti-patterns — MongoDB

Things the Reviewer flags and blocks.

- Giant documents approaching the 16MB limit — split or bucket.
- Unnecessary `$lookup` — you modeled relationally; embed instead.
- Duplicate collection for the same concept.
- A poor shard key (monotonic / low-cardinality) — hot shards.
- Documents/arrays with no growth bound.
- Treating Mongo like SQL (mental joins, heavy normalization).
