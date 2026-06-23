# ADR-0006: Unified end-to-end Pipeline

- **Status:** Accepted
- **Date:** 2026-06-21
- **Sprint:** AIES 4.0 (PR-7)

## Context
All engines existed independently (audit, plan, dispatch, context, execution,
review, delivery, learning, experience). The platform needs a single,
observable flow that runs them in order for any request, with no stage skipped.

## Decision
Add a **Pipeline** (`kernel/pipeline.py`) that wires one EventBus and drives:
`Audit → Plan → Dispatch → Context → Execute → Review → Deliver → Learn →
Brain.update → Experience.record`. Learning, Experience and (optional) ADR attach
to the bus as listeners, so the domain stages stay decoupled. The Dispatcher
chooses which agents become nodes; Context is built per selected agent;
Execution runs via the injected adapter (DryRunAdapter by default → safe).
Delivery runs only in `execute` mode. The `full-dev` Workflow (workflow/builtin)
declares this pipeline.

## Alternatives considered
- **Imperative one-off script.** Rejected: not reusable; the Workflow layer makes
  pipelines first-class and SDK-extensible.
- **Run all agents.** Rejected: the Dispatcher selects only what's needed.
- **Execute for real by default.** Rejected: unsafe; default is dry_run with the
  DryRunAdapter.

## Consequences
- New command `orchestrator.py pipeline "<goal>" [--mode] [--adr]`.
- One run produces: architecture summary, selected/skipped agents, per-agent
  context reduction, execution metrics, review counts, delivery gates (execute),
  brain version and experience KPIs.
- Backward compatible; the individual commands remain. Covered by the pipeline
  test suite (dry_run, execute+deliver, lifecycle events, experience persisted).
