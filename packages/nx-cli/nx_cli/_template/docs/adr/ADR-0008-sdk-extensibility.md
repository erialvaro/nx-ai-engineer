# ADR-0008: SDK — first-class extensibility (Agents/Engines/Workflows/Adapters/Plugins/Tools)

- **Status:** Accepted
- **Date:** 2026-06-21
- **Sprint:** AIES 4.0 (PR-9)

## Context
The platform must be extensible for years without touching its core
(architecture decision #9). Extension points existed implicitly; they needed a
single, stable, documented surface.

## Decision
`aies/sdk/__init__.py` exposes registries and lookups for **Agents, Engines,
Workflows, Adapters, Plugins and Tools**, plus `on(event, handler)` for
observers. Key wiring:
- `register_workflow` also publishes to the live `default_registry`, so the
  pipeline/CLI immediately see it.
- `register_plugin` runs the plugin's `setup(sdk)` hook, letting one plugin bundle
  agents+engines+workflows+tools.
- `apply_event_handlers(bus)` attaches SDK observers to the Pipeline's bus at
  start.
- `reset()` restores defaults (clean test/runtime isolation).
Contracts to implement live in their modules (`AgentAdapter`, `BaseEngine`,
`SelectionStrategy`, context `Resolver`, `SemanticIndex`). Documented in
`docs/sdk.md`.

## Alternatives considered
- **Entry-points/plugin discovery via packaging.** Rejected: adds packaging
  complexity and dependencies; explicit registration is simpler and portable.
- **Editing the core to add capability.** Rejected: violates Open/Closed and the
  "evolve for years without touching the core" goal.

## Consequences
- Third parties extend via `from aies import sdk`; the core stays dependency-free
  and unchanged.
- A future `MLStrategy` or vector `SemanticIndex` drops in through the same
  surface. Covered by the SDK test suite.
