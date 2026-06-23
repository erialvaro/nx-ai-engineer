# Policies — Testing Strategy

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Follow the test pyramid: many unit, fewer integration, few e2e.
- Tests are deterministic and isolated (no shared state, no real network).
- Cover new branches and edge cases; assert behavior, not implementation.
- Contract tests guard service boundaries.
- CI gates merges on the full suite + coverage threshold.
