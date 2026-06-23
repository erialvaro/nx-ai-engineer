# ADR-0005: Governance (quality gates/policies/checklists) and Delivery Engine

- **Status:** Accepted
- **Date:** 2026-06-21
- **Sprint:** AIES 4.0 (PR-6)

## Context
Reviewed work must be consolidated safely and consistently, and the platform
needs enforceable pre-conditions (tests on sensitive code, no protected-path
edits, no failed nodes) before anything ships.

## Decision
1. **Governance** (`governance/`): `quality_gates.py` (boolean, reasoned gates —
   protected paths, tests-on-critical, no-failed-nodes, plus an `evaluate()`
   aggregator), `policies.py` (core + project `domain_rules`), `checklists.py`
   (per-stage/agent checklists). Governance is consulted as preconditions and
   never mutates code.
2. **Delivery Engine** (`engines/delivery.py` + `deliver` command): runs the
   consolidated review, evaluates gates, writes a filled `PR-<task>.md` (impact,
   gates, risks, rollback), and — only if gates pass — releases the task's locks.
   Emits `delivery.completed`.

## Alternatives considered
- **Gates inside each engine.** Rejected: scatters policy; Governance centralizes
  it and stays Open/Closed.
- **Auto-merge on green.** Rejected for now: delivery packages and gates; the
  human/CI performs the merge. Keeps the platform advisory at the boundary.

## Consequences
- New command `orchestrator.py deliver --plan <id>`; blocks (exit 1) when a gate
  fails, surfacing the blocking gate.
- Delivery feeds the Learning Engine via `delivery.completed`.
- Covered by the delivery/governance test suite. Additive and backward compatible.
