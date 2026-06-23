# Context — Testing Strategy

Favor fast deterministic unit tests, add integration/contract tests at boundaries, and gate merges on the suite.

## Non-negotiables
- Follow the test pyramid: many unit, fewer integration, few e2e.
- Tests are deterministic and isolated (no shared state, no real network).
- Cover new branches and edge cases; assert behavior, not implementation.
- Contract tests guard service boundaries.
- CI gates merges on the full suite + coverage threshold.

## Always verify
- New code covered by tests
- Tests deterministic/isolated
- Edge cases asserted
- Contract tests at boundaries
- CI gate green
