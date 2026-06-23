"""Delivery Engine — consolidate reviewed work into a shippable change.

Validates quality gates, generates a filled pull_request.md (impact, risks,
rollback), releases the task's locks and updates status. It never implements a
feature — it packages what the agents produced. Runs read-only against the repo
except for releasing locks and writing the PR artifact.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from nx_core import locks as locks_mod
from nx_core import review as review_mod
from nx_core.foundation import util
from nx_core.governance import quality_gates as gates


def _pr_path(task_id: str) -> Path:
    return util.config_root() / "reviews" / f"PR-{task_id}.md"


def build_pr(task: dict, review: dict, gate_report: dict) -> str:
    L: list[str] = []
    a = L.append
    a(f"# PR — {task['id']}: {task.get('description', '')}")
    a("")
    a("## Summary")
    a(task.get("description", "—"))
    a("")
    a("## Changed files")
    for f in review.get("files", [])[:50]:
        a(f"- `{f}`")
    if not review.get("files"):
        a("- (no diff detected)")
    a("")
    a("## Impact")
    a(f"- Files changed: {review.get('total_changed', 0)}")
    a(f"- Critical/sensitive: {', '.join(review.get('critical_changes', [])) or 'none'}")
    a(f"- Without tests: {len(review.get('without_tests', []))}")
    a("")
    a("## Quality gates")
    for g in gate_report["gates"]:
        a(f"- [{'x' if g['passed'] else ' '}] {g['name']} — {g['reason']}")
    a("")
    a("## Risks")
    for f in review.get("critical_changes", []) or ["none flagged"]:
        a(f"- {f}")
    a("")
    a("## Rollback")
    a("Revert the integration commit / down-migration / feature flag as applicable.")
    a("")
    return "\n".join(L)


def deliver(task: dict, config: dict, *, base: str = "HEAD", bus=None,
            release_locks: bool = True) -> dict[str, Any]:
    """Consolidate a task: gate-check the diff, write the PR, release locks."""
    review = review_mod.build(base, config)
    gate_results = [
        gates.protected_paths_gate(review.get("files", []), config.get("protected_paths", [])),
        gates.tests_present_gate(review),
    ]
    gate_report = gates.evaluate(gate_results)

    pr_md = build_pr(task, review, gate_report)
    pr_path = _pr_path(task["id"])
    util.write_text(pr_path, pr_md)

    released = 0
    if release_locks and gate_report["passed"]:
        released = locks_mod.release(task=task["id"])

    result = {
        "task": task["id"],
        "gates_passed": gate_report["passed"],
        "blocking": gate_report["blocking"],
        "pr_path": str(pr_path),
        "locks_released": released,
        "rollback": "revert integration commit / down-migration / feature flag",
    }
    if bus is not None:
        bus.emit("delivery.completed", result)
    return result
