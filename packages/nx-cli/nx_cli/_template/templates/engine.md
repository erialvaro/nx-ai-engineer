# Engine: <Name>

> Guide for adding a new engine to `tools/aies/`. Engines are single-
> responsibility, stdlib-only, side-effect-light modules the orchestrator wires
> together.

## Responsibility
One sentence — the single thing this engine does.

## Public functions
- `build(...) -> dict` — pure computation, returns data.
- `render(report) -> str` — (optional) human-readable output.
- `run_and_persist(...) -> dict` — orchestrate + write to `.ai-project-assistant/...`.

## Rules
- Stdlib only. No network, no third-party deps.
- Read inputs via `aies.util` (paths, IO, git). Never hardcode paths.
- Pure functions where possible; isolate IO in `run_and_persist`.
- Don't mutate product code — engines analyze/plan/report only.

## Wiring
1. Add the module under `tools/aies/`.
2. Add a `cmd_*` handler + subparser in `tools/orchestrator.py`.
3. Document the command in `README.md` and `docs/workflow.md`.
4. Add a smoke test.
