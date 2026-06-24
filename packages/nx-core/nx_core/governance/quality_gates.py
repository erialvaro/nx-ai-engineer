"""Quality gates — boolean pre-conditions that can block a workflow step.

A gate inspects a context (a review report, a plan, a diff summary) and returns
pass/fail with a reason. Governance is cross-cutting: gates are *consulted* by
the Workflow/Delivery as preconditions; they never mutate anything.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class GateResult:
    name: str
    passed: bool
    reason: str


Gate = Callable[[dict], GateResult]


def protected_paths_gate(changed: list[str], protected: list[str]) -> GateResult:
    hits = [f for f in changed if any(fnmatch.fnmatch(f, p) for p in protected)]
    if hits:
        return GateResult("protected-paths", False,
                          f"protected paths modified: {', '.join(hits[:5])}")
    return GateResult("protected-paths", True, "no protected paths touched")


def tests_present_gate(review: dict) -> GateResult:
    without = review.get("without_tests", [])
    critical = review.get("critical_changes", [])
    # Critical/sensitive code must have tests.
    risky = [f for f in critical if f in set(without)]
    if risky:
        return GateResult("tests-on-critical", False,
                          f"sensitive files without tests: {', '.join(risky[:5])}")
    return GateResult("tests-on-critical", True, "critical changes are tested")


def no_failed_nodes_gate(run: dict) -> GateResult:
    nodes = run.get("nodes", [])
    failed = [n.get("id", "?") for n in nodes if n.get("state") == "FAILED"]
    if failed:
        return GateResult("no-failed-nodes", False, f"failed nodes: {', '.join(failed)}")
    return GateResult("no-failed-nodes", True, "all nodes succeeded")


def evaluate(gates: list[GateResult]) -> dict[str, Any]:
    failed = [g for g in gates if not g.passed]
    return {
        "passed": not failed,
        "gates": [{"name": g.name, "passed": g.passed, "reason": g.reason} for g in gates],
        "blocking": [g.name for g in failed],
    }
