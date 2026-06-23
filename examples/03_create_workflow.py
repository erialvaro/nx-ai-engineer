"""Example 3 — Create and register a reusable Workflow.

Run: python examples/03_create_workflow.py
"""
from _bootstrap import aies_home  # noqa: F401

import nx_sdk as sdk
from nx_core.kernel.engine import ExecutionMode
from nx_workflow.workflow import Step, Workflow, default_registry

# A small, reusable pipeline: audit then review (both read-only).
audit_review = Workflow("audit-review", (
    Step("audit", engine="audit", mode=ExecutionMode.DRY_RUN),
    Step("review", engine="review", mode=ExecutionMode.DRY_RUN, depends_on=("audit",)),
))

if __name__ == "__main__":
    # Register via the SDK — it also lands in the live default registry.
    sdk.register_workflow(audit_review)

    print("registered workflows:", default_registry().names())
    wf = sdk.get_workflow("audit-review")
    print("steps:", wf.step_names())
    print("first step engine:", wf.steps[0].engine, "mode:", wf.steps[0].mode.value)
