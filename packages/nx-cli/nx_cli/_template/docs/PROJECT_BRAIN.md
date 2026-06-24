# Project Brain

The **Project Brain** is the platform's persistent, project-specific knowledge,
stored as specialized directories under `.ai-project-assistant/brain/`. It holds
**knowledge, never code** — a `looks_like_code` guard drops any code-like value.

> Related: [memory.md](memory.md) (memory subsystem overview), ADR-0004 (Brain),
> ADR-0012 (Autonomous Learning).

## Layout (facets)
```
.ai-project-assistant/brain/
├── architecture/   discovered stack/frameworks (snapshots)
├── modules/        modules/workspaces
├── services/       services + contracts
├── apis/           endpoints/contracts
├── database/       schema/entities/migrations (metadata)
├── workflows/      per-workflow success statistics
├── patterns/       recurring agent sets, failure-prone agents, hot areas
├── history/        append-only event log
├── knowledge/      consolidated knowledge (+ semantic index)
├── bugs/           failure knowledge (counts/areas, not code)
├── decisions/      decision summaries
├── retrospectives/ append-only rich retrospectives (one per run)
├── adr/            Architecture Decision Records
└── version.json    monotonic version (bumps on every write)
```

## API (`aies.memory.brain.ProjectBrain`)
```python
brain.put(facet, key, record)   # key/value facets, incremental merge
brain.get(facet, key=None)      # one record or all in a facet
brain.append(facet, record)     # append-only facets (history/retrospectives/…)
brain.read_log(facet)           # read an append-only facet
brain.trim_log(facet, keep)     # cap a log (used by the Brain Optimizer)
brain.version()                 # current version
brain.migrate_legacy()          # import the old monolithic memory file
```

## How it updates (automatically)
After each **pipeline** run, the **Self Improvement Engine** assembles a
retrospective (time, failures, rework, agents used, files changed, decisions,
strategy success) and:
1. **Knowledge Evolution** records it + updates per-workflow success stats,
   decisions and failure knowledge (version bumps).
2. **Pattern Discovery** writes recurring agent sets / failure-prone agents /
   hot areas into `patterns/`.
3. **Similar-Task Detection** (re)indexes past requests for recommendations.
4. **Brain Optimizer** periodically caps the append-only logs.

Inspect what was learned:
```
nxai insights
nxai recommend "Add OAuth logout"
```

## Guarantees
- **Never stores code** (paths/counts/outcomes only; the guard enforces it).
- **Versioned & incremental** — every write bumps `version.json`.
- **Bounded** — logs are trimmed by the optimizer; no unbounded growth.
- **Portable** — plain JSON/JSONL; safe to commit (no secrets/PII — see
  [lgpd.md](lgpd.md)).
