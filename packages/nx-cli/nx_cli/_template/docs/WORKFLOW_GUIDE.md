# Workflow Guide

A **Workflow** is a reusable pipeline: an ordered set of `Step`s, each naming an
engine and the mode to run it in. Workflows are *data*, decoupled from who runs
them — the Pipeline/Execution layer executes them.

> Distinct from [workflow.md](workflow.md), which describes the **mandatory
> process** (audit→…→report). This guide is about authoring **Workflow objects**.

## Model (`aies.workflow.workflow`)
```python
from nx_workflow.workflow import Workflow, Step, default_registry
from nx_core.kernel.engine import ExecutionMode

wf = Workflow("audit-only", (
    Step("audit", engine="audit", mode=ExecutionMode.DRY_RUN),
))
```
- `Step(name, engine, mode, depends_on=())` — one stage.
- `Workflow(name, steps)` — immutable; `step_names()` lists stages.
- `WorkflowRegistry` — `register(wf)`, `get(name)`, `names()`.

## Builtins (`workflow/builtin.py`)
- **`full-dev`** — Audit → Plan → Dispatch → Context → Execute → Review → Deliver.
- **`plan-only`** — Audit → Plan → Dispatch.
- **`execute-plan`** — just execution.

The **Decision Engine** picks the workflow automatically (`full-dev` for code
changes, `plan-only` otherwise); see ADR-0011.

## Register a custom workflow (SDK)
```python
import nx_sdk as sdk
sdk.register_workflow(wf)        # also published to the live default_registry
sdk.get_workflow("audit-only")   # resolvable everywhere
```

## Guidance
- Order by dependency, not by convenience: contracts/data before code, QA and
  Review late, Delivery last.
- Keep steps single-engine; compose, don't conflate.
- A step's `mode` should respect safety: only the execution/delivery steps use
  `EXECUTE`; analysis steps use `DRY_RUN`.

A runnable example: `examples/03_create_workflow.py`.
