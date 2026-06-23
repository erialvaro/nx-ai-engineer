"""Intelligence · Estimation.

Estimates relative effort, blast radius and confidence for a plan, from the
number of involved agents/areas and the assessed risk. Heuristic and
deterministic — a planning aid and an input to Experience KPIs, not a promise.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import risk as risk_mod


@dataclass
class Estimate:
    effort_points: int          # rough size (Fibonacci-ish)
    blast_radius: int           # distinct areas/agents touched
    risk_level: str
    confidence: float           # 0..1; lower when risk is high or scope is wide

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__


_FIB = [1, 2, 3, 5, 8, 13, 21]


def _nearest_fib(n: int) -> int:
    for f in _FIB:
        if n <= f:
            return f
    return _FIB[-1]


def estimate(plan: Any, *, arch: dict | None = None, config: dict | None = None) -> Estimate:
    agents = list(getattr(plan, "involved_agents", []) or [])
    subtasks = list(getattr(plan, "subtasks", []) or [])
    areas = {a for s in subtasks for a in getattr(s, "areas", [])}
    blast = max(len(agents), len(areas))

    risks = risk_mod.analyze(getattr(plan, "description", ""), arch, config)
    rlevel = risk_mod.level(risks)
    rscore = risk_mod.score(risks)

    raw = len(agents) + len(areas) + rscore
    effort = _nearest_fib(raw)

    # Confidence drops with scope and risk.
    confidence = max(0.2, round(1.0 - 0.06 * blast - 0.05 * rscore, 2))
    return Estimate(effort_points=effort, blast_radius=blast,
                    risk_level=rlevel, confidence=confidence)


# Simple, transparent cost/time model (units are deliberately abstract).
_TOKENS_PER_POINT = 2000      # ≈ model tokens per effort point
_MINUTES_PER_POINT = 2        # ≈ wall-clock minutes per effort point (sequential)


class EstimationEngine:
    """Named engine wrapper that adds **cost** and **time** estimates on top of
    the effort model. Reuses `_nearest_fib`; no duplication of the core sizing."""

    name = "estimation"

    def assess(self, *, agents: list[str], risk_score: int = 0,
               parallelism: int = 1) -> dict[str, Any]:
        n = len(agents)
        effort = _nearest_fib(n + risk_score)
        time_seq = effort * _MINUTES_PER_POINT
        parallelism = max(1, parallelism)
        time_par = round(time_seq / parallelism, 1)
        confidence = max(0.2, round(1.0 - 0.05 * n - 0.04 * risk_score, 2))
        return {
            "effort_points": effort,
            "estimated_cost_tokens": effort * _TOKENS_PER_POINT,
            "estimated_time_min_sequential": time_seq,
            "estimated_time_min_parallel": time_par,
            "confidence": confidence,
        }
