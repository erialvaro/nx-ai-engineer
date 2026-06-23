# Engine Guide

Engines are AIES's unit of work. Every engine is single-responsibility,
stdlib-only, and obeys the mandatory **Dry Run → Test → Execute** contract.

> See also: `templates/engine.md` (checklist), ADR-0001 (Engine contract).

## The contract (`aies.kernel.engine`)
```python
from nx_core.kernel.engine import BaseEngine, EngineResult, ExecutionMode

class MyEngine(BaseEngine):
    name = "my-engine"

    def dry_run(self, ctx) -> EngineResult:   # simulate; ZERO side effects
        return EngineResult(ExecutionMode.DRY_RUN, ok=True, actions=[...])

    def test(self, ctx) -> EngineResult:      # validate safely; no prod effect
        return EngineResult(ExecutionMode.TEST, ok=True)

    def execute(self, ctx) -> EngineResult:   # real effect (only after dry+test)
        return EngineResult(ExecutionMode.EXECUTE, ok=True)
```
Always call `engine.run(ctx, mode)` (not the mode methods directly): the
`BaseEngine` **gate** refuses `EXECUTE` unless `DRY_RUN` and `TEST` passed for the
same `ctx` in this cycle. `run_full_cycle(ctx)` runs all three in order.

### Read-only engines
Analysis engines (Audit/Review-style) subclass `ReadOnlyEngine` and implement a
single `analyze(ctx)`; it satisfies all three modes safely.

## Events
Inject a bus to emit progress; engines should publish, never subscribe:
```python
MyEngine(bus=bus)          # emits engine.dry_run / engine.test / engine.execute
```
Governance/Observability/Experience/Learning subscribe — you don't wire them.

## Rules
- **Stdlib only**; read inputs via `aies.foundation.util` (paths/IO/git).
- **Pure where possible**; isolate IO. Never mutate product code directly —
  delegate real work to an injected runner/adapter (see the Execution Engine).
- **No upward imports**: domain engines must not import Governance/Observability/
  Experience (use events).

## Register it (so the platform/SDK can use it)
```python
import nx_sdk as sdk
sdk.register_engine("my-engine", MyEngine)
```

## Wire into the CLI/pipeline (optional)
Add a `cmd_*` handler + subparser in `orchestrator.py`, or reference the engine
from a `Workflow` step (see `WORKFLOW_GUIDE.md`). Add tests and an ADR if the
engine encodes an architectural decision.

A full runnable example: `examples/02_create_engine.py`.
