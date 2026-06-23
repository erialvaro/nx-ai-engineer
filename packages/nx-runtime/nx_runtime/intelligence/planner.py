"""Intelligence · Planner (logical home).

Re-exports the planner engine so new code can use `aies.intelligence.planner`
while `aies.planner` keeps working. Behavior is unchanged.
"""
from nx_core.planner import (  # noqa: F401
    Plan,
    Subtask,
    build_plan,
    execution_order,
)

__all__ = ["Plan", "Subtask", "build_plan", "execution_order"]
