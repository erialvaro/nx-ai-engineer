# Checklist — PostgreSQL

Review gate for any schema/data change.

- [ ] 1NF satisfied
- [ ] 2NF satisfied
- [ ] 3NF satisfied
- [ ] BCNF considered
- [ ] Primary key defined (and composite PK justified)
- [ ] Foreign keys + ON DELETE/UPDATE set
- [ ] Unique constraints where required
- [ ] Indexes for new query paths (non-redundant)
- [ ] EXPLAIN ANALYZE validated; cost acceptable
- [ ] Scalability/partition considered
- [ ] Migration reversible + backfill plan
- [ ] Tenant/owner isolation preserved
