# Checklist — Cassandra

Review gate for any schema/data change.

- [ ] One table per query
- [ ] Partition key spreads load
- [ ] Partition size bounded
- [ ] Clustering order set
- [ ] No ALLOW FILTERING
