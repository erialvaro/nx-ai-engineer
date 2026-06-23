# ADR-0011: Decision Engine — automatic architectural decisions at execution time

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0002 (Dispatcher), ADR-0006 (Pipeline), ADR-0010 (Cluster)

## Context
Choosing *how* to execute a request — which agents, which workflow, in what
order, with what risk/impact/cost/time, whether Review/QA are needed, and whether
it can run in parallel — was spread across the pipeline and implicit. We want a
single intelligence layer that makes these decisions automatically and
auditably, **reusing** the existing reasoning pieces rather than duplicating them.

## Decision
Add a **Decision Engine** (`intelligence/decision.py`) that composes four
collaborating engines, all in the `intelligence` layer:
- **Strategy Engine** (`strategy.py`) — *which agents* (reuses the Agent
  Dispatcher / its Strategy Pattern) and *which workflow* (policy over the
  Workflow registry: `full-dev` for code, `plan-only` otherwise).
- **Risk Engine** (`risk.py`, `RiskEngine`) — risk level/score/messages
  (wraps the existing risk functions; one source of truth).
- **Estimation Engine** (`estimation.py`, `EstimationEngine`) — effort, plus
  **estimated cost** (tokens) and **estimated time** (sequential and
  parallel-aware), reusing the effort model.
- **Reasoning Engine** (`reasoning.py`) — derives **need for Review**, **need for
  QA**, **parallelizable?**, a confidence, and a human-readable **rationale**.

The Decision Engine also computes **execution order** and **parallelism layers**
(topological layers of the selected agents — same layer ⇒ independent ⇒ runnable
concurrently). It returns a single `Decision` and emits `decision.made`
(+ `decision.recorded` → Governance ADR when requested).

The **Pipeline** now drives its agent-selection step from the Decision Engine
(which calls the dispatcher internally — no double work), exposing the full
decision in `PipelineResult.decision`. New CLI: `decide "<goal>" [--adr]`.

## Alternatives considered
- **Bake the decision into the dispatcher.** Rejected: the dispatcher's job is
  agent selection; workflow/risk/cost/time/parallelism are broader. Composition
  keeps each engine single-responsibility.
- **Reimplement risk/estimation inside the Decision Engine.** Rejected:
  duplication. `RiskEngine`/`EstimationEngine` are thin wrappers over the
  existing modules.
- **LLM-based decisions now.** Deferred: heuristics are deterministic, offline
  and stdlib-only; an `MLStrategy`/learned estimator can plug in later via the
  same interfaces.

## Consequences
- One call yields agents, skipped, workflow, order, parallelism layers + degree,
  risk level/messages, impact, estimated cost & time, Review/QA needs, confidence
  and rationale — all auditable (events + optional ADR).
- The parallelism degree the Decision Engine computes maps directly onto the
  Execution Cluster's `--workers` (ADR-0010).
- Backward compatible; the pipeline's observable outputs are unchanged plus a new
  `decision` field. Covered by `test_decision.py`. Full suite: 130 tests, green.
