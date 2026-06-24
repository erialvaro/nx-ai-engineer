# Patterns — MongoDB

- Embedding — store data read together in one document.
- Referencing — link when data is large, shared, or independently updated.
- Bucket pattern — group time-series/events into bounded buckets.
- Subset pattern — embed the hot subset, reference the rest.
- Computed/Outlier pattern — precompute; special-case rare large documents.
- Attribute pattern — index many similar attributes via an array of {k,v}.
- Polymorphic pattern — one collection for similar-but-varying shapes.
