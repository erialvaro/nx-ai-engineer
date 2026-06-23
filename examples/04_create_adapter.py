"""Example 4 — Create an Adapter (swap the model without touching the core).

An adapter is the ONLY boundary between AIES and an AI model/CLI. Implement
`run(...) -> AgentResult` and the Execution Engine/Cluster can use it.

Run: python examples/04_create_adapter.py
"""
from _bootstrap import aies_home  # noqa: F401

import nx_sdk as sdk
from nx_runtime.adapters.base import AgentAdapter
from nx_core.kernel.domain import AgentResult
from nx_core.kernel.engine import ExecutionMode
from nx_runtime.schedulers.execution import ExecutionEngine


class EchoAdapter:
    """A trivial, side-effect-free adapter that 'implements' by echoing."""
    name = "echo"

    def run(self, *, agent, context, instructions, mode=ExecutionMode.EXECUTE):
        if mode is ExecutionMode.DRY_RUN:
            return AgentResult(ok=True, notes=f"[dry] {agent}: {instructions}")
        return AgentResult(ok=True, changed_files=[], notes=f"{agent} did: {instructions}")


if __name__ == "__main__":
    print("satisfies AgentAdapter protocol:", isinstance(EchoAdapter(), AgentAdapter))
    sdk.register_adapter("echo", EchoAdapter())

    # Inject it into the Execution Engine (mode-aware; full cycle).
    engine = ExecutionEngine(adapter=sdk.get_adapter("echo"))
    plan = {"id": "demo", "subtasks": [
        {"agent": "backend", "objective": "build endpoint", "areas": [],
         "depends_on": [], "acceptance": []}]}
    result = engine.run_full_cycle(plan)
    print("execution ok:", result.ok, "| node:", result.actions[0]["state"])
