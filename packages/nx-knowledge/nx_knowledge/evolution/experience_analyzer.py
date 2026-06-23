"""Experience Analyzer — turns the Brain's retrospectives into insights.

Aggregates time, success/failure, rework, agent usage and per-workflow success
from the (rich) retrospectives the Self Improvement Engine records. Read-only.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from ..memory.brain import ProjectBrain


class ExperienceAnalyzer:
    name = "experience-analyzer"

    def analyze(self, brain: ProjectBrain | None = None) -> dict[str, Any]:
        brain = brain or ProjectBrain()
        retros = [r for r in brain.read_log("retrospectives") if r.get("agents_used")]
        if not retros:
            return {"runs": 0}

        durations = [r["duration_sec"] for r in retros if isinstance(r.get("duration_sec"), (int, float))]
        successes = sum(1 for r in retros if r.get("strategy_success"))
        total_tasks = sum(len(r.get("agents_used", [])) for r in retros)
        retries = sum(int(r.get("retries", 0)) for r in retros)
        failures = sum(int(r.get("failures", 0)) for r in retros)

        agent_freq = Counter(a for r in retros for a in r.get("agents_used", []))
        workflows = brain.get("workflows")  # {name: {runs, successes, success_rate}}

        return {
            "runs": len(retros),
            "avg_duration_sec": round(sum(durations) / len(durations), 2) if durations else None,
            "success_rate": round(successes / len(retros), 3),
            "rework_rate": round(retries / total_tasks, 3) if total_tasks else 0.0,
            "failures": failures,
            "agent_frequency": dict(agent_freq.most_common(10)),
            "workflow_success": {k: v.get("success_rate") for k, v in workflows.items()},
            "risk_distribution": dict(Counter(r.get("risk_level") for r in retros)),
        }
