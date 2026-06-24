# Context — MongoDB

Model documents for the application's read and write patterns — NOT like relational tables. Decide embedding vs referencing per access pattern. Never mentally 'join'; shape the document for how it is read. Bound array growth; pick a good shard key.

## Non-negotiables
- Never normalize like SQL — model for the access pattern, not for normal forms.
- Never design around a mental JOIN — prefer embedding the data read together.
- Always evaluate Embedding vs Referencing explicitly for each relationship.
- Always think about the read pattern (and the write pattern) before modeling.
- Bound array/document growth — never let a document grow unbounded.
- Choose a shard key that spreads writes and matches query routing.

## Always verify
- Embedding vs referencing decided per relationship
- Read patterns drive the document shape
- Write patterns considered
- No unbounded arrays/documents
- Compound indexes match query shape
- Shard key spreads load and routes queries
