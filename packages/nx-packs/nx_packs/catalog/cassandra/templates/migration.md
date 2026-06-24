# Cassandra — migration template

## Forward
```
-- forward migration
```

## Rollback
```
-- reversible rollback
```

## Review
- [ ] Existing entity/table reused (no duplicate)
- [ ] Indexes considered + non-redundant
- [ ] EXPLAIN/cost validated
- [ ] Reversible; backfill plan for non-null/renames
