"""Workflow — reusable execution pipelines (the layer between Kernel and
Schedulers). A Workflow is data: an ordered set of Steps, each naming an engine
and the mode to run it in. The Execution Engine consumes a Workflow; new
workflows are added via the SDK without changing the core.

This PR ships the minimal model + a builtin `execute-plan` workflow. The full
`full-dev` pipeline arrives with PR-7.
"""
from __future__ import annotations

from dataclasses import dataclass

from nx_core.kernel.engine import ExecutionMode


@dataclass(frozen=True)
class Step:
    name: str
    engine: str
    mode: ExecutionMode = ExecutionMode.DRY_RUN
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class Workflow:
    name: str
    steps: tuple[Step, ...] = ()

    def step_names(self) -> list[str]:
        return [s.name for s in self.steps]


class WorkflowRegistry:
    def __init__(self) -> None:
        self._wf: dict[str, Workflow] = {}

    def register(self, wf: Workflow) -> Workflow:
        self._wf[wf.name] = wf
        return wf

    def get(self, name: str) -> Workflow:
        if name not in self._wf:
            raise KeyError(f"unknown workflow '{name}'")
        return self._wf[name]

    def names(self) -> list[str]:
        return sorted(self._wf)

    def clear(self) -> None:
        """Drop all registered workflows (reset state between runs/tests)."""
        self._wf.clear()


# Builtin workflows.
EXECUTE_PLAN = Workflow(
    name="execute-plan",
    steps=(Step("execute", engine="execution", mode=ExecutionMode.EXECUTE),),
)

_DEFAULT = WorkflowRegistry()
_DEFAULT.register(EXECUTE_PLAN)


def default_registry() -> WorkflowRegistry:
    return _DEFAULT
