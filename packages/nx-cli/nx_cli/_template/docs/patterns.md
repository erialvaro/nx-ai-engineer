# Architectural Patterns

> Record the recurring patterns this project uses so agents reuse them instead
> of inventing new ones. Discovery seeds some of this (frameworks, layering);
> fill in the rest as you learn the codebase.

## How we do things here
- **Layering:** (e.g. controller → service → repository) —
- **Validation:** (where/how inputs are validated) —
- **Error model:** (exceptions vs result types, error shapes) —
- **Config & secrets:** (where config lives, how secrets are injected) —
- **API style:** (REST/GraphQL/RPC, versioning, pagination) —
- **State management (frontend):** —
- **AI/LLM:** (prompt storage, model selection, eval approach) —
- **Async/jobs:** (queues, schedulers) —

## Reusable building blocks (don't re-create these)
- …

## Anti-patterns to avoid in this repo
- Duplicating an existing service/endpoint.
- Bypassing the validation/auth layer.
- Opportunistic refactors outside the task scope.
