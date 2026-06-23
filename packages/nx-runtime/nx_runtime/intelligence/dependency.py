"""Intelligence · Dependency analysis (logical home).

Today dependency ordering lives in the planner (`execution_order` + the
`_DEPENDS_ON` edges). This module gives it a stable, dedicated import path and
will grow into a full Dependency Engine (DAG, cycle detection at plan level) in
its own PR, without breaking callers.
"""
from nx_core.planner import execution_order  # noqa: F401

__all__ = ["execution_order"]
