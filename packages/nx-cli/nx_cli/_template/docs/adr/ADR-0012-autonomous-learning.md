# ADR-0012: Autonomous Learning — the platform evolves from its own use

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0004 (Brain/Learning/Experience/Semantic), ADR-0006
  (Pipeline), ADR-0011 (Decision Engine)

## Context
The platform recorded basic retrospectives but did not truly *learn*: it didn't
capture time/rework/strategy-success, mine recurring patterns, detect similar
past tasks, or recommend approaches. We want continuous self-improvement that
updates the Project Brain automatically after each run — storing **knowledge,
never code** — and reusing the existing Memory/Experience/Semantic layers.

## Decision
Add an **Autonomous Learning** layer (`aies/evolution/`) of seven collaborating
components, all built on the existing infrastructure:
- **SelfImprovementEngine** — subscribes to the bus and, per pipeline run,
  accumulates the required signals (**time, failures, rework, agents used, files
  changed, decisions, strategy success**) from `pipeline.started`,
  `decision.made`, `task.completed/failed/retrying`, `review.completed`,
  `run.completed`, `delivery.completed`, then on `pipeline.completed` assembles a
  retrospective and orchestrates the rest. Emits `improvement.learned` /
  `brain.updated`.
- **KnowledgeEvolution** — incremental, versioned consolidation into the Brain
  (retrospectives + per-workflow success stats + decisions + failure knowledge).
- **PatternDiscovery** — mines recurring agent sets, failure-prone agents and hot
  file areas; writes them to the `patterns` facet.
- **SimilarTaskDetector** — finds similar past tasks via the Semantic index
  (rebuilt from retrospectives; vector index swappable via the SDK).
- **RecommendationEngine** — recommends agents/workflow from similar tasks +
  aggregated experience, with warnings (e.g. historically high rework).
- **ExperienceAnalyzer** — aggregates KPIs/trends from the Brain.
- **BrainOptimizer** — bounds the append-only logs (via a new `Brain.trim_log`)
  so the Brain stays compact.

The **Pipeline** now uses `SelfImprovementEngine` instead of the basic
`LearningEngine` (richer retrospective; the old engine remains a standalone
component). `pipeline.completed` is emitted **before** reading the Brain version
so learning is reflected. New CLI: `insights`, `recommend "<goal>"`.

## Alternatives considered
- **Extend LearningEngine in place.** Rejected: learning now spans many events
  and several engines; a dedicated layer keeps each piece single-responsibility.
  LearningEngine stays for simple use.
- **Store diffs/snippets to "learn from code".** Rejected: the Brain must never
  hold code. We store metadata (paths, counts, outcomes) — the code guard stays.
- **Train an ML model now.** Deferred: heuristics + the Semantic interface are
  enough today; a learned recommender/estimator plugs in later via the SDK.
- **Persist a separate learning store.** Rejected: reuse the Project Brain
  (directory facets) and the Experience/Semantic layers — no new persistence.

## Consequences
- After every pipeline run the Brain auto-updates with a rich retrospective and
  derived patterns/stats; `insights` and `recommend` expose the accumulated
  knowledge; recommendations improve as history grows.
- Brain growth is bounded by the optimizer; knowledge-only guarantee preserved.
- Backward compatible (additive engines/commands; pipeline outputs unchanged plus
  learning side effects). Covered by `test_evolution.py`. Full suite: 141 tests,
  green.
