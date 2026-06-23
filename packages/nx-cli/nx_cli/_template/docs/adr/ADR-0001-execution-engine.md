# ADR-0001: Execution Engine and the mandatory Dry Run → Test → Execute contract

- **Status:** Accepted
- **Date:** 2026-06-21
- **Sprint:** AIES 2.0 — S1 (PR-2)

## Context
AIES 1.0 could audit, plan, lock, worktree and review, but could not **execute**
a plan. We need an engine that drives a plan's subtasks to completion while
remaining (a) generic — no knowledge of agents or of Claude Code — and (b) safe —
incapable of mutating project code by accident. Architecture decision #2 further
requires that **every** engine pass through Dry Run → Test → Execute before any
real change.

## Decision
1. Introduce a **Kernel** (`domain`, `states`, `lifecycle`, `engine`) providing
   the task state machine (9 states), the dependency-aware `TaskGraph`, and a
   `BaseEngine` whose `run(ctx, mode)` **enforces** the mode gate: `EXECUTE`
   requires `DRY_RUN` + `TEST` to have passed for the same context.
2. The **Execution Engine** (`schedulers/execution.py`) subclasses `BaseEngine`.
   It schedules ready nodes (deps COMPLETED, not locked), runs them via an
   **injected `runner`/Adapter**, and controls retries, failures, blocking,
   cancellation and progress through state transitions.
3. Work is delegated to an **`AgentAdapter`**. The default is the
   **`DryRunAdapter`**, which changes nothing — so even `execute` is safe until a
   real adapter is explicitly injected. This satisfies "the Execution Engine
   never depends on Claude Code".
4. Decoupling is via an in-process **EventBus**: the engine publishes `run.*` /
   `task.*` / `engine.*` events; Governance, Observability and Experience only
   subscribe.

## Alternatives considered
- **Engine calls agents directly.** Rejected: couples the core to a model and
  breaks the "generic execution" requirement.
- **Execute by default, dry-run opt-in.** Rejected: unsafe; violates decision #2.
- **External workflow engine / dependency (e.g. Airflow, Celery).** Rejected:
  breaks the stdlib-only, zero-dependency principle and portability.
- **Threaded/parallel scheduler now.** Deferred: synchronous scheduling is
  simpler, deterministic and testable; parallelism can be added behind the same
  API later without breaking callers.

## Consequences
- New CLI command: `orchestrator.py run --plan <id> [--mode dry_run|test|execute]`
  (default `dry_run`).
- Runs persist to `.ai-project/runs/<id>.json` (resumable, auditable).
- The mode gate is enforced centrally, so future engines inherit the safety
  guarantee for free.
- Backward compatible: all prior commands and imports unchanged; everything here
  is additive. Verified by the compat + kernel + execution test suites.
- Next (PR-3): the **Agent Dispatcher** will choose *which* agents become nodes,
  feeding this engine.
