"""Kernel domain model — the immutable-ish data the platform moves around.

None of these types ever carry project source code (Brain/Experience store
knowledge, not code). `Plan`/`Subtask` mirror the planner's output so the
Execution Engine can consume a plan without importing the planner.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from .states import ExecutionState


@dataclass
class Subtask:
    id: str
    agent: str
    objective: str = ""
    areas: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)


@dataclass
class Node:
    """A schedulable wrapper around a Subtask, carrying execution state."""
    subtask: Subtask
    state: ExecutionState = ExecutionState.PENDING
    attempts: int = 0
    max_retries: int = 1
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    @property
    def id(self) -> str:
        return self.subtask.id

    @property
    def depends_on(self) -> list[str]:
        return self.subtask.depends_on

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "agent": self.subtask.agent, "state": self.state.value,
            "attempts": self.attempts, "max_retries": self.max_retries,
            "error": self.error, "result": self.result,
        }


@dataclass
class Run:
    id: str
    plan_id: str
    nodes: list[Node] = field(default_factory=list)
    status: str = "created"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    metrics: dict[str, Any] = field(default_factory=dict)

    def node(self, node_id: str) -> Optional[Node]:
        return next((n for n in self.nodes if n.id == node_id), None)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "plan_id": self.plan_id, "status": self.status,
            "started_at": self.started_at, "ended_at": self.ended_at,
            "metrics": self.metrics, "nodes": [n.as_dict() for n in self.nodes],
        }


@dataclass
class AgentContext:
    """Minimal context handed to an agent (produced by the Context Engine)."""
    agent: str
    subtask_id: str
    files: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    apis: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    docs: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentResult:
    ok: bool
    changed_files: list[str] = field(default_factory=list)
    notes: str = ""
    error: Optional[str] = None
    duration_ms: int = 0


def subtasks_from_plan(plan: Any) -> list[Subtask]:
    """Adapt a planner `Plan` (or a plain dict) into kernel Subtasks.

    Planner subtasks are keyed by `agent`; we derive a stable id from it so the
    dependency graph (which references agents) resolves directly.
    """
    raw = getattr(plan, "subtasks", None)
    if raw is None and isinstance(plan, dict):
        raw = plan.get("subtasks", [])
    out: list[Subtask] = []
    for s in raw or []:
        agent = getattr(s, "agent", None) if not isinstance(s, dict) else s.get("agent")
        objective = getattr(s, "objective", "") if not isinstance(s, dict) else s.get("objective", "")
        areas = getattr(s, "areas", []) if not isinstance(s, dict) else s.get("areas", [])
        deps = getattr(s, "depends_on", []) if not isinstance(s, dict) else s.get("depends_on", [])
        acc = getattr(s, "acceptance", []) if not isinstance(s, dict) else s.get("acceptance", [])
        out.append(Subtask(id=agent, agent=agent, objective=objective,
                           areas=list(areas), depends_on=list(deps), acceptance=list(acc)))
    return out
