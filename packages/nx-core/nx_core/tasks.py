"""Task Engine — render a Plan into a durable Markdown task file.

Task files are the contract handed to executing agents. They live under
`.ai-project/tasks/<id>.md` and embed a machine-readable JSON block so the
orchestrator (review, status) can re-read them without re-planning.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from . import locks as locks_mod
from . import util
from .planner import Plan, execution_order


def tasks_dir() -> Path:
    return util.ensure_dir(util.config_root() / "tasks")


def render(plan: Plan, task_id: str, conflicts: list[dict[str, Any]]) -> str:
    order = execution_order(plan)
    machine = {
        "id": task_id,
        "description": plan.description,
        "priority": plan.priority,
        "agents": plan.involved_agents,
        "order": order,
        "subtasks": [asdict(s) for s in plan.subtasks],
        "status": "planned",
        "created_at": util.now_iso(),
    }

    lines: list[str] = []
    a = lines.append
    a(f"# Task {task_id}")
    a("")
    a(f"> **Priority:** {plan.priority}  |  **Status:** planned  |  **Created:** {util.now_iso()}")
    a("")
    a("## Objective")
    a(plan.description)
    a("")
    a("## Agents involved")
    a(", ".join(plan.involved_agents) or "—")
    a("")
    a("## Execution order")
    a(" → ".join(order) or "—")
    a("")

    if conflicts:
        a("## ⚠️ Lock conflicts")
        a("Another task already holds these paths. Coordinate before starting:")
        for c in conflicts:
            a(f"- `{c.get('requested', c.get('path'))}` held by task `{c.get('task')}` ({c.get('owner')})")
        a("")

    a("## Subtasks")
    for s in plan.subtasks:
        a(f"### {s.agent}")
        a(f"- **Objective:** {s.objective}")
        a(f"- **Candidate areas:** {', '.join(f'`{x}`' for x in s.areas) or '—'}")
        a(f"- **Depends on:** {', '.join(s.depends_on) or '—'}")
        a("- **Acceptance:**")
        for ac in s.acceptance:
            a(f"  - [ ] {ac}")
        a("")

    a("## Risks")
    for r in plan.risks:
        a(f"- {r}")
    if not plan.risks:
        a("- None identified by the planner — verify manually.")
    a("")

    a("## Global acceptance criteria")
    for ac in plan.acceptance:
        a(f"- [ ] {ac}")
    a("")

    a("## Checklist")
    for step in [
        "Re-read the relevant agent spec(s) in `.ai-project/agents/`",
        "Confirm no forbidden files are touched",
        "Implement incrementally",
        "Run tests",
        "Self-review against acceptance criteria",
        "Update docs / changelog",
    ]:
        a(f"- [ ] {step}")
    a("")

    a("<!-- AIES:DATA")
    a(json.dumps(machine, ensure_ascii=False, indent=2))
    a("AIES:DATA -->")
    a("")
    return "\n".join(lines)


def create(plan: Plan, task_id: str, owner: str = "orchestrator") -> dict[str, Any]:
    """Persist the task file, register advisory locks for candidate areas."""
    areas = sorted({a for s in plan.subtasks for a in s.areas})
    conflicts = locks_mod.conflicts_for(areas, owner_task=task_id) if areas else []

    content = render(plan, task_id, conflicts)
    path = tasks_dir() / f"{task_id}.md"
    util.write_text(path, content)

    for area in areas:
        agent_owner = next((s.agent for s in plan.subtasks if area in s.areas), owner)
        locks_mod.acquire(area, task_id, agent_owner)

    return {"path": str(path), "id": task_id, "conflicts": conflicts, "locked": areas}


def load(task_id: str) -> dict[str, Any] | None:
    path = tasks_dir() / f"{task_id}.md"
    text = util.read_text(path)
    if not text:
        return None
    start = text.find("<!-- AIES:DATA")
    end = text.find("AIES:DATA -->")
    if start == -1 or end == -1:
        return None
    blob = text[start + len("<!-- AIES:DATA"): end].strip()
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return None


def list_tasks() -> list[dict[str, Any]]:
    out = []
    for f in sorted(tasks_dir().glob("*.md")):
        data = load(f.stem)
        if data:
            out.append({"id": data["id"], "priority": data.get("priority"),
                        "status": data.get("status"), "agents": data.get("agents", [])})
    return out
