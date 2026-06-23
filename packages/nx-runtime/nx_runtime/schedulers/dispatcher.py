"""Agent Dispatcher — selects ONLY the agents a task needs.

Given a goal, it decides which agents become work nodes (and which are skipped),
in what order, and why. Selection is a pluggable **Strategy** (rule-based today;
an `MLStrategy` can drop in later behind the same interface without touching the
core). Example: "Implement OAuth" → architect, security, backend, database, qa,
reviewer, delivery — never frontend.

It feeds the Execution Engine but does not execute anything itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from nx_core import agents as agents_mod
from nx_core.agents import CANON_ORDER  # single source of truth; re-exported here

# Dependency edges used to order/scope the selected agents.
DEPENDS_ON = {
    "backend": ["database", "security", "architect"],
    "ai": ["backend"],
    "frontend": ["backend"],
    "devops": ["backend", "database"],
    "qa": ["backend", "frontend", "ai", "database", "security"],
    "reviewer": ["backend", "frontend", "ai", "database", "security", "devops", "qa"],
    "delivery": ["reviewer"],
    "docs": ["delivery"],
}

# Selecting an agent implies others are needed (e.g. auth needs persistence).
IMPLIES = {
    "security": ["backend", "database"],
    "ai": ["backend"],
    "database": ["backend"],
}

# Always part of a change (quality + delivery gates).
ALWAYS = ["qa", "reviewer", "delivery"]

# Meta agents are orchestration, never dispatched as workers.
META = {"planner", "task-manager"}


@dataclass
class AgentSelection:
    agent: str
    selected: bool
    reason: str
    order: int = -1
    depends_on: list[str] = field(default_factory=list)


@runtime_checkable
class SelectionStrategy(Protocol):
    name: str

    def select(self, *, description: str, registry: dict) -> list[AgentSelection]:
        """Return the SELECTED agents (selected=True), ordered, with reasons.
        The dispatcher fills in the skipped ones."""
        ...


class RuleBasedStrategy:
    name = "rule-based"

    def select(self, *, description: str, registry: dict) -> list[AgentSelection]:
        text = description.lower()
        reasons: dict[str, str] = {}

        # 1) keyword matches over non-meta agents.
        for name, agent in registry.items():
            if name in META or name in ALWAYS:
                continue
            hits = [kw for kw in agent.keywords if kw in text]
            if hits:
                reasons[name] = f"matched: {', '.join(hits)}"

        # 2) implications.
        for src in list(reasons):
            for implied in IMPLIES.get(src, []):
                reasons.setdefault(implied, f"required by {src}")

        # 3) architect joins when there are multiple implementing areas.
        implementers = [a for a in reasons if a not in ALWAYS and a != "architect"]
        if len(implementers) >= 2:
            reasons.setdefault("architect", "multiple areas — needs design")

        # 4) always-on quality/delivery gates.
        for a in ALWAYS:
            if a in registry:
                reasons.setdefault(a, "always included (quality/delivery gate)")

        ordered = sorted(reasons, key=lambda a: CANON_ORDER.index(a) if a in CANON_ORDER else 99)
        selected_set = set(ordered)
        out = []
        for i, a in enumerate(ordered):
            deps = [d for d in DEPENDS_ON.get(a, []) if d in selected_set]
            out.append(AgentSelection(agent=a, selected=True, reason=reasons[a],
                                      order=i, depends_on=deps))
        return out


class AgentDispatcher:
    def __init__(self, strategy: SelectionStrategy | None = None, *, bus=None) -> None:
        self._strategy = strategy or RuleBasedStrategy()
        self._bus = bus

    @property
    def strategy_name(self) -> str:
        return getattr(self._strategy, "name", "custom")

    def dispatch(self, *, description: str, config: dict | None = None) -> list[AgentSelection]:
        registry = agents_mod.registry(config or {})
        selected = self._strategy.select(description=description, registry=registry)
        selected_names = {s.agent for s in selected}

        # Compose skipped entries for the remaining (non-meta) agents.
        skipped = [
            AgentSelection(agent=name, selected=False,
                           reason="not required by this goal")
            for name in registry
            if name not in selected_names and name not in META
        ]
        skipped.sort(key=lambda s: s.agent)

        if self._bus:
            self._bus.emit("agent.selected", {
                "strategy": self.strategy_name,
                "selected": [s.agent for s in selected],
                "skipped": [s.agent for s in skipped],
            })
        return selected + skipped

    @staticmethod
    def selected(selections: list[AgentSelection]) -> list[AgentSelection]:
        return [s for s in selections if s.selected]
