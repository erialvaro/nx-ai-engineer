"""Decision Engine — the intelligence layer that decides, automatically, how a
request should be executed.

It composes the other reasoning engines (Strategy, Risk, Estimation, Reasoning)
into a single `Decision`:
  - which agents to use (and which to skip)
  - which workflow to use
  - execution order + parallelism layers
  - risks, impact
  - estimated cost & time
  - need for Review / QA
  - whether the work is parallelizable

It reuses the Agent Dispatcher, Risk/Estimation engines and the dependency model
— no selection/risk/sizing logic is reimplemented here. It emits `decision.made`
(and, on request, `decision.recorded` so Governance writes an ADR).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from ..schedulers.dispatcher import CANON_ORDER, AgentSelection
from .estimation import EstimationEngine
from .reasoning import ReasoningEngine
from .risk import RiskEngine
from .strategy import StrategyEngine


@dataclass
class Decision:
    request: str
    agents: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    workflow: str = "full-dev"
    execution_order: list[str] = field(default_factory=list)
    parallel_layers: list[list[str]] = field(default_factory=list)
    parallelism: int = 1
    parallelizable: bool = False
    risk_level: str = "minimal"
    risks: list[str] = field(default_factory=list)
    impact: dict[str, Any] = field(default_factory=dict)
    estimated_cost_tokens: int = 0
    estimated_time_min: float = 0.0
    needs_review: bool = True
    needs_qa: bool = True
    confidence: float = 0.5
    rationale: list[str] = field(default_factory=list)
    selections: list[AgentSelection] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        d = dict(self.__dict__)
        d.pop("selections", None)  # not JSON-friendly; kept only in-process
        return d


def _layers(selections: list[AgentSelection]) -> list[list[str]]:
    """Topological layers of the selected agents; agents in the same layer have
    no mutual dependency and can run in parallel."""
    sel = {s.agent: list(s.depends_on) for s in selections if s.selected}
    level: dict[str, int] = {}

    def lvl(a: str) -> int:
        if a in level:
            return level[a]
        deps = [d for d in sel.get(a, []) if d in sel]
        level[a] = 0 if not deps else 1 + max(lvl(d) for d in deps)
        return level[a]

    for a in sel:
        lvl(a)
    buckets: dict[int, list[str]] = {}
    for a, l in level.items():
        buckets.setdefault(l, []).append(a)
    order_key = lambda x: CANON_ORDER.index(x) if x in CANON_ORDER else 99
    return [sorted(buckets[k], key=order_key) for k in sorted(buckets)]


class DecisionEngine:
    name = "decision"

    def __init__(self, *, bus=None) -> None:
        self._bus = bus
        self.strategy = StrategyEngine(bus=bus)
        self.risk = RiskEngine()
        self.estimation = EstimationEngine()
        self.reasoning = ReasoningEngine()

    def decide(self, request: str, *, arch: Optional[dict] = None,
               config: Optional[dict] = None, record_adr: bool = False) -> Decision:
        config = config or {}
        # 1) Strategy: which agents + which workflow.
        selections = self.strategy.select_agents(request, config)
        agents = [s.agent for s in selections if s.selected]
        skipped = [s.agent for s in selections if not s.selected]
        workflow = self.strategy.select_workflow(request, selections)

        # 2) Order + parallelism from the dependency layers.
        layers = _layers(selections)
        execution_order = [a for layer in layers for a in layer]
        parallelism = max((len(layer) for layer in layers), default=1)

        # 3) Risk.
        risk = self.risk.assess(request, arch, config)

        # 4) Estimation (cost/time), aware of parallelism.
        est = self.estimation.assess(agents=agents, risk_score=risk["score"],
                                     parallelism=parallelism)

        # 5) Reasoning: review / qa / parallelizable + rationale.
        reasoned = self.reasoning.reason(
            request=request, agents=agents, risk_level=risk["level"],
            risk_messages=risk["messages"], parallelism=parallelism, estimate=est)

        decision = Decision(
            request=request, agents=agents, skipped=skipped, workflow=workflow,
            execution_order=execution_order, parallel_layers=layers,
            parallelism=parallelism, parallelizable=reasoned["parallelizable"],
            risk_level=risk["level"], risks=risk["messages"],
            impact={"blast_radius": len(agents), "affected_agents": agents,
                    "risk_level": risk["level"]},
            estimated_cost_tokens=est["estimated_cost_tokens"],
            estimated_time_min=est["estimated_time_min_parallel"],
            needs_review=reasoned["needs_review"], needs_qa=reasoned["needs_qa"],
            confidence=reasoned["confidence"], rationale=reasoned["rationale"],
            selections=selections,
        )

        if self._bus is not None:
            self._bus.emit("decision.made", decision.summary())
            if record_adr:
                self._bus.emit("decision.recorded", {
                    "title": f"Execution decision for: {request[:60]}",
                    "context": f"Risk {decision.risk_level}; {len(agents)} agents; "
                               f"workflow {workflow}.",
                    "decision": "Agents: " + ", ".join(agents) +
                                f" | order: {' -> '.join(execution_order)}",
                    "consequences": decision.rationale,
                })
        return decision
