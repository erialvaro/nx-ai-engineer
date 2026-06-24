# Architecture — PostgreSQL

Normalize to 3NF/BCNF by default; denormalize deliberately for read paths with a documented trade-off. Drive indexing from real query plans (EXPLAIN ANALYZE). Keep tenant isolation and referential integrity enforced in the database.
