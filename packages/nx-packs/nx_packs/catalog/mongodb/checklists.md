# Checklist — MongoDB

Review gate for any schema/data change.

- [ ] Embedding vs referencing decided per relationship
- [ ] Read patterns drive the document shape
- [ ] Write patterns considered
- [ ] No unbounded arrays/documents
- [ ] Compound indexes match query shape
- [ ] Shard key spreads load and routes queries
- [ ] TTL set where data expires
- [ ] Aggregation `$lookup` is justified (not a SQL join in disguise)
