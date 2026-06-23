"""Strategy Engine — decides *which agents* and *which workflow* to use.

Reuses the Agent Dispatcher (the existing Strategy Pattern for agent selection)
and the Workflow registry; it adds the workflow-choice policy on top. No agent
selection logic is duplicated here.
"""
from __future__ import annotations

from typing import Optional

from ..schedulers.dispatcher import AgentDispatcher, AgentSelection
from nx_workflow.workflow import default_registry

# Agents whose presence implies real code changes (→ full pipeline).
_CODE_AGENTS = {"backend", "frontend", "database", "ai", "security", "devops"}


class StrategyEngine:
    name = "strategy"

    def __init__(self, *, dispatcher: Optional[AgentDispatcher] = None, bus=None) -> None:
        self._dispatcher = dispatcher or AgentDispatcher(bus=bus)

    @property
    def strategy_name(self) -> str:
        return self._dispatcher.strategy_name

    def select_agents(self, request: str, config: dict | None = None) -> list[AgentSelection]:
        return self._dispatcher.dispatch(description=request, config=config or {})

    def select_workflow(self, request: str, selections: list[AgentSelection]) -> str:
        chosen = {s.agent for s in selections if s.selected}
        text = (request or "").lower()
        names = set(default_registry().names())

        if chosen & _CODE_AGENTS:
            wf = "full-dev"
        elif any(w in text for w in ("review", "audit only", "analyze")):
            wf = "review-only" if "review-only" in names else "plan-only"
        else:
            wf = "plan-only"
        return wf if wf in names else "full-dev"
