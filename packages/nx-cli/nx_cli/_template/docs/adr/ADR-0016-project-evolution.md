# ADR-0016: Project Evolution — structured knowledge enrichment after each execution

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0012 (Autonomous Learning), ADR-0004 (Project Brain),
  ADR-0013 (Knowledge Providers)

## Context
Autonomous Learning recorded run-level retrospectives (time/failures/rework/
agents/files/decisions/strategy success), but it did not turn each execution into
**structured project knowledge** — which modules/services/APIs/entities/tests/
integrations/dependencies were impacted, which patterns apply, which bugs were
fixed, which decisions and lessons resulted. We want every agent execution to
enrich that knowledge automatically — storing **knowledge only**, never code and
never model responses.

## Decision
Add a **Project Evolution** engine (`evolution/project_evolution.py`). After each
execution (called by the Self Improvement Engine during `learn()`), it classifies
the run's **changed file paths and metadata** — never by reading code — into the
Project Brain facets:
- **modules** (top-level dirs, excluding dot/config dirs), **services**, **APIs**,
  **entities** (`database`), **tests**, **integrations**, **dependencies**
  (manifests) — key/value facets with an `impacted` counter and `last_goal`;
- **architectural patterns** (from the discovered architecture frameworks);
- **fixed bugs** (when a fix-style goal succeeds), **technical decisions**
  (from the structured decision), **lessons learned** (from failures/retries or
  success), and a consolidated **evolution** record with **related files (paths
  only)**.

To support this, the Brain gains four facets: `tests`, `integrations`,
`dependencies`, `lessons`.

### Guarantees
- **Never stores code** — only paths, names, counts and structured metadata. The
  Brain's `looks_like_code` guard is a second line of defense (verified by tests).
- **Never stores model responses** — agent output text is never passed here; the
  classifier reads paths/metadata, not `AgentResult.notes`.
- Deterministic and offline; it does not interpret code or generate answers.

`insights` now reports the accrued structured knowledge (per-facet counts).

## Alternatives considered
- **Parse code to extract services/entities/APIs.** Rejected: violates
  "never interpret code / never store code". Path/metadata classification is
  sufficient and safe.
- **Store the agent's explanation/output as knowledge.** Rejected: "never store
  model responses". We store only structured, derived facts.
- **One giant evolution record.** Rejected: per-facet key/value records make the
  knowledge queryable and let impact counts accumulate over time.

## Consequences
- After each pipeline run the Brain accrues structured knowledge across 13+
  categories; the Obsidian vault (Services/APIs/Modules/Dependencies/…) reflects
  it automatically. `insights` shows the counts.
- Backward compatible and additive (new facets, new engine, wired into existing
  learning). Covered by `test_project_evolution.py`. Full suite green; no cycles.
