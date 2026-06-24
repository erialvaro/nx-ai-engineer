# Migration Guide

AIES follows [Semantic Versioning](https://semver.org). The platform is
**backward compatible** through the 1.0 → 5.0 line: legacy imports and CLI
commands keep working. This guide records how to upgrade and what (if anything)
changes.

## Upgrading an installed project
`.ai-project-assistant/` is a portable copy of `framework/`. To pick up a new framework
version without losing your data:

```bash
# idempotent: copies new/updated files, never clobbers your config/brain/tasks
nxai init
```

- Your `config.json`, `brain/`, `tasks/`, `runs/` and `memory/` are preserved.
- New runtime folders (e.g. `brain/`, `experience/`, `logs/`) are created on
  demand; their absence never breaks older commands.
- The Project Brain auto-migrates the legacy `memory/architecture.json` into the
  directory-based `brain/architecture/` on first run (the old file is kept).

## Compatibility guarantees
- **Imports:** the platform's modules are imported from the `nx_*` packages —
  e.g. `from nx_core import analyzer, planner, locks, review, tasks, worktree,
  config, agents, util`.
- **CLI:** all prior commands (`audit, plan, review, worktree, tasks, locks,
  unlock, status`) are unchanged; new commands are additive. The CLI is `nxai`
  (the legacy `nx` alias is also installed).
- **Data:** on-disk formats are forward-compatible; new keys are optional with
  defaults.

## Version map
| Version | Adds | Notes |
|---------|------|-------|
| 1.0 | audit/plan/review/locks/worktrees | baseline |
| 2.0 | `run`, `dispatch` (Execution + Dispatcher) | Dry Run→Test→Execute gate |
| 3.0 | `context` (Context Engine, Brain, Learning) | dir-based Brain migration |
| 4.0 | `pipeline`, `deliver`, `metrics`, `decide`, `insights`, `recommend` | autonomous |
| 5.0-rc1 | quality gate, docs, examples; SemVer | no feature changes |

## Breaking changes
- **None** through 5.0. Any future breaking change will land only in a new
  **major** version, be listed in `CHANGELOG.md`, and ship with a migration note
  here. Deprecations will warn for one minor cycle before removal.

## Rollback
The framework writes only inside `.ai-project-assistant/` and creates git
worktrees/branches on request. To roll back, restore the previous
`.ai-project-assistant/tools/` (or re-run `nxai update` from the previous framework copy);
your tasks/brain remain intact.
