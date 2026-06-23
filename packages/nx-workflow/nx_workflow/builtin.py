"""Builtin workflows — reusable pipelines registered with the default registry.

`full-dev` is the canonical end-to-end pipeline (architecture §18). Steps are
declarative; the Pipeline (kernel/pipeline.py) executes them with the right
engines. New workflows can be registered via the SDK without code changes.
"""
from __future__ import annotations

from nx_core.kernel.engine import ExecutionMode
from .workflow import Step, Workflow, default_registry

FULL_DEV = Workflow(
    name="full-dev",
    steps=(
        Step("audit", engine="audit", mode=ExecutionMode.DRY_RUN),
        Step("plan", engine="planner", mode=ExecutionMode.DRY_RUN, depends_on=("audit",)),
        Step("dispatch", engine="dispatcher", mode=ExecutionMode.DRY_RUN, depends_on=("plan",)),
        Step("context", engine="context", mode=ExecutionMode.DRY_RUN, depends_on=("dispatch",)),
        Step("execute", engine="execution", mode=ExecutionMode.EXECUTE, depends_on=("context",)),
        Step("review", engine="review", mode=ExecutionMode.DRY_RUN, depends_on=("execute",)),
        Step("deliver", engine="delivery", mode=ExecutionMode.EXECUTE, depends_on=("review",)),
    ),
)

PLAN_ONLY = Workflow(
    name="plan-only",
    steps=(
        Step("audit", engine="audit"),
        Step("plan", engine="planner", depends_on=("audit",)),
        Step("dispatch", engine="dispatcher", depends_on=("plan",)),
    ),
)


def register_builtins() -> None:
    reg = default_registry()
    for wf in (FULL_DEV, PLAN_ONLY):
        reg.register(wf)


register_builtins()
