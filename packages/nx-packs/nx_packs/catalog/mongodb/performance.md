# Performance — MongoDB

- Aggregation pipeline — push work into the database; stage order matters.
- `$lookup` — only when referencing is the right model; index the foreign field.
- Projection — return only needed fields.
- Compound index — order fields by equality → sort → range.
- Shard key — spread writes, enable targeted (not scatter-gather) queries.
- Replica set — read/write concerns for durability vs latency.
- TTL index — auto-expire ephemeral data.
