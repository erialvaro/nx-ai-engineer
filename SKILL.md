---
name: nx-ai-engineer
description: NX AI Engineer — a Developer Infrastructure Platform for AI-assisted development (installed CLI `nxai`). Use when the user wants to plan/execute a development goal through a disciplined audit→plan→implement→review pipeline, coordinate multiple AI agents (backend/frontend/db/ai/security/devops/qa/reviewer) on one codebase, set up `.ai-project-assistant`, or asks to "use NX AI Engineer / nxai / the platform / orchestrator / AIES / multi-agent workflow / plan a feature safely". Works on any stack (Node, Python, Go, monorepos/Nx, etc.) — it auto-discovers the architecture.
---

# NX AI Engineer

A Developer Infrastructure Platform that turns any AI model into a coordinated,
multi-agent development team. It is **project-agnostic**: it discovers the stack at
runtime and never assumes any technology. The platform installs as the `nxai` CLI;
each project keeps a single **data-only** `.ai-project-assistant/` folder.

## ⛔ MANDATORY RULE — never implement immediately

Every development request handled with this skill **must** follow this workflow.
No stage may be skipped:

1. **Audit** the existing architecture (no assumptions).
2. **Discover** reusable components & existing patterns.
3. **Impact analysis** — what could break, blast radius.
4. **Risk identification** — security, data, compatibility, tenant/PII.
5. **Planning** — decompose the goal.
6. **Subtasks** — one owner each, no overlap.
7. **Assign agents** responsible.
8. **Order** by dependencies.
9. **Implement incrementally** (in worktree lanes).
10. **Run tests.**
11. **Code review** (consolidated).
12. **Consolidate.**
13. **Document.**
14. **Final report.**

The framework produces **plans, scaffolding and reports — never product code by
itself.** You (and the specialized agents) implement; the framework keeps the
work audited, scoped, coordinated and reviewed.

## When to use this skill
- The user gives a development goal and wants it planned/executed safely
  ("implement OAuth", "add export to CSV", "refactor the billing module").
- The user mentions: AIES, the framework, the orchestrator, multi-agent
  workflow, `.ai-project-assistant`, agent lanes, "plan a feature", "audit the project".
- Any non-trivial change to an unfamiliar or shared codebase where scope
  discipline and review matter.

For a one-line answer or a trivial edit, you don't need the full pipeline.

## How to use it

### 0. Locate or install the platform
- Preferred (installed): `pip install nx-ai-engineer`, then run `nxai` from the
  project root. If the project has no `.ai-project-assistant/` yet, run `nxai init`.
- From this skill checkout (no install): use the in-repo shim, e.g.
  `python <skill>/framework/tools/orchestrator.py <command>`, or bootstrap with
  `python <skill>/scripts/init_aies.py <project-dir>` (delegates to `nxai init`).
- All commands below are written as `nxai <command>`; with the source shim,
  substitute `python <skill>/framework/tools/orchestrator.py <command>`.

### 1. Audit (always first)
```
nxai audit
```
Discovers stack/frameworks/monorepo/tests/CI and writes
`.ai-project-assistant/memory/`. Read the strengths and risks before planning.

### 2. Plan a goal
```
nxai plan "Add OAuth login with Google"
```
Creates a task under `.ai-project-assistant/tasks/<id>.md` with: involved agents,
dependency-ordered subtasks, candidate files, risks, acceptance criteria, and
advisory file locks (with conflict detection).

### 3. Open isolated lanes (optional, for parallel agents)
```
nxai worktree --plan <task-id>
```
Creates one git worktree per implementing agent (`feature/<agent>`). Idempotent.

### 4. Implement
For each subtask in order, **read the agent's spec** in `.ai-project-assistant/agents/<agent>.md`,
stay inside its allowed paths, and follow `.ai-project-assistant/PROJECT_RULES.md`. Spawn a
subagent per lane if working in parallel.

### 5. Review
```
nxai review
```
Consolidated report: ownership, untested changes, large files, sensitive
changes, protected-path violations, lock overlap. Saved to `.ai-project-assistant/reviews/`.

### 6. Consolidate, document, report
Integrate lanes, update docs, release locks
(`nxai unlock --task <id>`), and produce the final report
(summary, files changed, impact, risks, rollback, next steps).

### 7. Or run the whole thing at once (platform pipeline)
```
nxai pipeline "<goal>" [--mode dry_run|test|execute]
```
Runs the full flow — Audit → Plan → Dispatch → Context → Execute → Review →
Deliver → Learn → Brain → Experience — on one event bus. Safe by default
(`dry_run`, DryRunAdapter: no code is changed). `--mode execute` also packages a
PR and updates the Project Brain.

## Command reference
| Command | Purpose |
|---------|---------|
| `audit` | Discover & persist the architecture |
| `plan "<goal>"` | Decompose into a task (agents, subtasks, risks, locks) |
| `decide "<goal>"` | Full execution decision: agents, workflow, order, risk, impact, cost/time, Review/QA, parallelism |
| `dispatch "<goal>"` | Select only the agents a goal needs (Strategy) |
| `context --plan <id> --agent <a>` | Build the minimal context for an agent |
| `run --plan <id> [--mode]` | Execute a task (Dry Run → Test → Execute) |
| `review [--base REF]` | Consolidated diff review |
| `deliver --plan <id>` | Gate-check, write the PR, release locks |
| `pipeline "<goal>" [--mode]` | Full end-to-end flow (all engines) |
| `metrics` | Show persisted KPIs + telemetry |
| `insights` | What the platform has learned (success/rework/patterns) |
| `recommend "<goal>"` | Recommend agents/workflow from past learning |
| `knowledge index\|list\|retrieve` | Inspect Knowledge Providers (read-only) |
| `knowledge sync\|status` | Coordinate/inspect the three memories (Brain/Obsidian/Git) |
| `obsidian sync\|status` | Sync/inspect the Obsidian vault (visual view of the Brain) |
| `worktree <agent>` / `--plan <id>` | Isolated git worktree lanes |
| `tasks` · `locks` · `unlock` · `status` | Task/lock/overview utilities |

## Platform layers (`packages/nx-*`)
- **kernel** — domain, states (9-state machine), lifecycle (DAG), `BaseEngine`
  with the mandatory **Dry Run → Test → Execute** gate.
- **workflow** — reusable pipelines (`full-dev`, `plan-only`).
- **schedulers** — Execution Engine (sequential) + **Execution Cluster**
  (concurrent worker pool: queue, scheduler, priorities, per-worker lifecycle;
  `run/pipeline --workers N`) + Agent Dispatcher.
- **intelligence** — Planner, Dependency, Risk, Estimation, plus the **Decision
  Engine** (`decide` command): auto-decides agents, workflow, order, risk, impact,
  cost/time, Review/QA need and parallelism — composing Strategy/Risk/Estimation/
  Reasoning engines.
- **knowledge** — the **Project Knowledge Engine** has exactly five
  responsibilities (`discover`, `index`, `relate`, `update`, `deliver_context`)
  and **no reasoning** — all intelligence belongs to the model; it only reduces
  cognitive load (richer history → fewer tokens). See `docs/PROJECT_KNOWLEDGE.md`.
  It coordinates the three memories (**Brain**=operational, **Obsidian**=
  organizational, **Git**=historical) and is the access point the Context Engine
  retrieves through. **Knowledge Providers**:
  no source is coupled to the Context Engine; everything flows through a provider
  (Filesystem, Git, Markdown, ADR, Project-Brain, Obsidian). Providers only index/catalog/retrieve/enrich/relate —
  never decide, interpret code or generate answers. Command: `knowledge`.
  **Obsidian** is a visual representation of the Brain: `ObsidianSync` auto-renders
  a navigable, backlinked vault (categories + index + relationship map),
  incrementally, on each run. Command: `obsidian`.
- **memory** — Context Engine (consumes Knowledge Providers), Learning Engine,
  **Project Brain** (directory-based), Semantic Knowledge (stub for vector search).
- **evolution** — **Autonomous Learning** + **Project Evolution**: after each run
  the platform learns (time, failures, rework, agents, files, patterns, decisions,
  strategy success) AND enriches structured knowledge — classifying changed
  paths/metadata into Brain facets (modules, services, APIs, entities, tests,
  integrations, dependencies, patterns, fixed bugs, decisions, lessons, related
  files). Knowledge only — never code, never model responses.
  Self Improvement + Experience Analyzer + Pattern Discovery + Similar-Task
  Detection + Recommendation + Knowledge Evolution + Brain Optimizer. Commands:
  `insights`, `recommend`.
- **governance** — ADR, policies, quality gates, checklists.
- **experience** — usage KPIs (success/rework/reduction…).
- **observability** — event bus, structured logs, telemetry.
- **adapters** — `DryRunAdapter` (default, safe) + **`ClaudeCodeAdapter`** (real
  execution via the Claude Code CLI; mode-aware, timeout/retry/cancel). Select
  with `run`/`pipeline --adapter claude-code`. The core stays model-agnostic.
- **sdk** — register Agents/Engines/Workflows/Adapters/Plugins/Tools (see
  `docs/sdk.md`). Extend without touching the core.

## Configuration
`.ai-project-assistant/config.json` (optional, all keys have defaults):
- `domain_rules` — project invariants surfaced into every plan (e.g. tenant
  isolation, PII handling).
- `protected_paths` — globs no agent may modify (review blocks on them).
- `extra_agents` / `disabled_agents` — extend or trim the agent roster.
- `branch_prefix`, `default_base`, `large_file_loc`.

## Layout of `.ai-project-assistant/`
- `agents/` — one spec per agent (responsibilities, allowed/forbidden paths,
  checklist). `tools/aies/agents.py` holds the machine-routable globs/keywords.
- `engines` — `tools/aies/`: analyzer, planner, dependency, tasks, locks,
  review, worktree (stdlib-only, single-responsibility).
- `docs/` — workflow, architecture, coding-standards, patterns, tenant-rules,
  lgpd, memory. Reuse existing project docs; never duplicate.
- `templates/` — task, review, pull_request, engine, agent.
- `tasks/`, `reviews/`, `locks/`, `memory/` — runtime artifacts.
- `PROJECT_RULES.md` — non-negotiable rules.

## Extending
- **New agent:** copy `agents/_TEMPLATE.md`, register globs/keywords in
  `tools/aies/agents.py` or `config.json > extra_agents`.
- **New engine:** follow `templates/engine.md`; add a `cmd_*` + subparser in
  `orchestrator.py`. The core never changes — engines plug in.

See `README.md` in this skill for the full reference and design rationale.
