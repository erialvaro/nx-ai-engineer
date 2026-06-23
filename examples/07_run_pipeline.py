"""Example 7 — Run the full pipeline end-to-end (programmatically).

audit -> decide -> context -> execute -> review -> deliver -> learn

Uses the safe DryRunAdapter, so nothing is changed. Run:
    python examples/07_run_pipeline.py
"""
from _bootstrap import aies_home  # noqa: F401

from nx_core.kernel.engine import ExecutionMode
from nx_runtime.kernel.pipeline import Pipeline

if __name__ == "__main__":
    # max_workers>1 would use the concurrent Execution Cluster.
    pipeline = Pipeline(max_workers=2)
    result = pipeline.run("Implement OAuth login with tokens",
                          mode=ExecutionMode.DRY_RUN)

    print("architecture:  ", result.architecture or "(empty project)")
    print("selected agents:", result.selected_agents)
    print("skipped agents: ", result.skipped_agents)
    print("decision wf:    ", result.decision.get("workflow"))
    print("parallelism:    ", result.decision.get("parallelism"))
    print("execution:      ", result.execution.get("status"),
          result.execution.get("metrics"))
    print("brain version:  ", result.brain_version)
    print("experience:     ", result.experience)
