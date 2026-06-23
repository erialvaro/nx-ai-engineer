# ADR-0002: Agent Dispatcher with a pluggable selection Strategy

- **Status:** Accepted
- **Date:** 2026-06-21
- **Sprint:** AIES 2.0 — S2 (PR-3)

## Context
The Execution Engine (ADR-0001) runs whatever nodes it is given. Something must
decide **which** agents a goal actually needs — running every agent on every task
is wasteful and wrong (e.g. an OAuth change should not invoke the frontend
agent). The selection logic must be replaceable: rules today, machine learning
later, without changing the rest of the platform.

## Decision
1. Add an **Agent Dispatcher** (`schedulers/dispatcher.py`) that, given a goal,
   returns the **selected** agents — ordered by dependencies, each with a reason
   — plus the **skipped** ones (so the decision is auditable).
2. Selection is a **Strategy** (`SelectionStrategy` Protocol). `RuleBasedStrategy`
   ships now and combines: keyword matches from the agent registry, **implication
   rules** (e.g. `security` ⇒ `backend`, `database`), always-on quality/delivery
   gates (`qa`, `reviewer`, `delivery`), and an `architect` when multiple
   implementing areas are involved. A future `MLStrategy` implements the same
   interface and drops in via the SDK.
3. The dispatcher publishes `agent.selected`; meta agents (`planner`,
   `task-manager`) are never dispatched as workers.

## Alternatives considered
- **Reuse the planner's agent list directly.** Rejected as the sole source: the
  planner optimizes task decomposition; selection needs its own rules (e.g. auth
  implying persistence) and an auditable selected/skipped view. The dispatcher
  may select a superset and remains the authority for *who runs*.
- **Hardcode an if/else selector.** Rejected: not swappable; blocks the ML path.
- **LLM-based selection now.** Deferred: violates determinism/offline and the
  zero-dependency principle; the Strategy interface keeps the door open.

## Consequences
- New CLI command: `orchestrator.py dispatch "<goal>"` (or `--plan <id>`) showing
  selected (ordered, with reasons + deps) and skipped agents.
- The Execution Engine will consume the dispatcher's selection in the unified
  pipeline (PR-7); until then `dispatch` is usable standalone.
- Backward compatible and additive; covered by the dispatcher test suite.
- Example verified: "Implement OAuth login with tokens" → architect, security,
  backend, database, qa, reviewer, delivery — **frontend skipped**.
