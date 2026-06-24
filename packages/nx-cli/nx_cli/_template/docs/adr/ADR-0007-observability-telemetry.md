# ADR-0007: Observability — structured logging and telemetry

- **Status:** Accepted
- **Date:** 2026-06-21
- **Sprint:** AIES 4.0 (PR-8)

## Context
Runs need to be inspectable and measurable: a durable event log and live KPIs
(failures, retries, completion, deliveries) without coupling the engines to any
logging concern.

## Decision
Add `observability/logging.py` (`EventLogger` — every event as one JSON line in
`.ai-project-assistant/logs/events.jsonl`) and `observability/telemetry.py` (`Telemetry` —
event counters + a KPI snapshot exported to `.ai-project-assistant/metrics/telemetry.json`).
Both are **pure `*` subscribers** attached by the Pipeline. A new `metrics`
command surfaces the persisted Experience KPIs and the telemetry snapshot.

## Alternatives considered
- **`logging` stdlib module / external APM.** Rejected: JSONL is simpler,
  dependency-free and machine-readable; external APM breaks portability.
- **Engines log themselves.** Rejected: couples domain logic to logging; the
  event bus keeps it orthogonal (Open/Closed).

## Consequences
- New command `orchestrator.py metrics`.
- Pipeline now writes `logs/events.jsonl`, `metrics/telemetry.json` and
  `experience/summary.json` per run.
- Observability (runtime counts) stays distinct from Experience (durable,
  over-time KPIs). Covered by the observability test suite.
