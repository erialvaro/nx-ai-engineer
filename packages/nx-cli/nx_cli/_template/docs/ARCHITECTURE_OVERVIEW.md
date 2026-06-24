# Architecture Overview

A one-page map of AIES. For the full design see [ARCHITECTURE.md](ARCHITECTURE.md)
and the decision records in [adr/](adr/).

## Layers (dependencies point downward; no cycles)
```
SDK            register Agents/Engines/Workflows/Adapters/Plugins/Tools
───────────────────────────────────────────────────────────────────────
Governance · Observability · Experience        (cross-cutting; event subscribers)
───────────────────────────────────────────────────────────────────────
Kernel        domain · states(9) · lifecycle(DAG) · BaseEngine(Dry→Test→Execute)
  └ Pipeline  composition root (wires everything; the only "imports-all" module)
Workflow      reusable pipelines (full-dev, plan-only)
Schedulers    Execution Engine (sequential) · Execution Cluster (concurrent) · Dispatcher
Intelligence  Planner · Dependency · Risk · Estimation · Strategy · Reasoning · Decision
Memory        Context · Learning · Project Brain (dir) · Semantic
Evolution     Autonomous Learning (self-improvement, patterns, similarity, recommend, …)
Engines       Audit · Review · Delivery
───────────────────────────────────────────────────────────────────────
Adapters      DryRunAdapter (default) · ClaudeCodeAdapter · (future models)
Foundation    util · config
```

## Key contracts (stable APIs)
| Contract | Module | Implement to add… |
|----------|--------|-------------------|
| `AgentAdapter` | `adapters/base.py` | a new model/CLI |
| `BaseEngine` (Dry→Test→Execute) | `kernel/engine.py` | a new engine |
| `SelectionStrategy` | `schedulers/dispatcher.py` | agent-selection policy (rules→ML) |
| `Resolver` | `memory/context.py` | a context resolver |
| `SemanticIndex` | `memory/semantic.py` | vector/keyword search |
| `Workflow` | `workflow/workflow.py` | a reusable pipeline |

## Core guarantees
- **Stdlib-only** core; **zero** third-party dependencies.
- **Model-agnostic**: the core never imports a specific model — only `AgentAdapter`.
- **Safe by default**: Dry Run → Test → Execute; `DryRunAdapter` changes nothing.
- **Knowledge, never code** in the Project Brain.
- **Event-driven**: engines publish; Governance/Observability/Experience/Learning
  only subscribe — so they can be added without touching domain engines.

## On-disk contract (per project)
`.ai-project-assistant/` — `tasks/ reviews/ locks/ runs/ memory/ brain/ knowledge/
context-cache/ experience/ logs/ metrics/`, plus `agents/ docs/ templates/
tools/` and `config.json`.

## Flow
`request → Audit → Decide(agents/workflow/order/risk/cost/parallelism) → Context →
Execute (engine or cluster) → Review → Deliver → Learn → Brain.update`.
