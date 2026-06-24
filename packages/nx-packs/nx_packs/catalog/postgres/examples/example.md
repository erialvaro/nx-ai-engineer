# Example — PostgreSQL

Reuse before create: a request for a `clients` table finds an existing `customers` entity — extend it instead of duplicating. A case-insensitive email lookup gets an expression index `ON customers (lower(email))`, validated index-only via EXPLAIN ANALYZE.
