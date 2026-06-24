# Rules — MongoDB

Enforceable rules. The Database Reviewer blocks a change that violates these; the Engineering Contract surfaces them to the agent.

- Never normalize like SQL — model for the access pattern, not for normal forms.
- Never design around a mental JOIN — prefer embedding the data read together.
- Always evaluate Embedding vs Referencing explicitly for each relationship.
- Always think about the read pattern (and the write pattern) before modeling.
- Bound array/document growth — never let a document grow unbounded.
- Choose a shard key that spreads writes and matches query routing.
- Index the queries you actually run; avoid unused/duplicate indexes.
