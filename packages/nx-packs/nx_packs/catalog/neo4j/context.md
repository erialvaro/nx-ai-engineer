# Context — Neo4j

Engineering standard for Neo4j. Graph modeling on Neo4j: nodes/relationships, traversal performance.

## Non-negotiables
- Model the domain as nodes + relationships (not tables).
- Index the properties you match on.
- Bound traversal depth; avoid cartesian products.
- Use relationships instead of foreign keys.

## Always verify
- Nodes/relationships modeled
- Property indexes/constraints
- Traversal bounded
- PROFILE validated
- No super-node hotspots
