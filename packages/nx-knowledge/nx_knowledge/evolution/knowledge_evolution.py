"""Knowledge Evolution — incremental, versioned consolidation of a run's
retrospective into the Project Brain. Stores knowledge, never code; every write
bumps the Brain version (handled by the Brain itself)."""
from __future__ import annotations

from typing import Any

from ..memory.brain import ProjectBrain


class KnowledgeEvolution:
    name = "knowledge-evolution"

    def __init__(self, brain: ProjectBrain | None = None) -> None:
        self.brain = brain or ProjectBrain()

    def evolve(self, retro: dict[str, Any]) -> int:
        """Record the retrospective and update derived facets. Returns new version."""
        self.brain.append("retrospectives", retro)

        # Per-workflow success statistics.
        wf = retro.get("workflow")
        if wf:
            stats = self.brain.get("workflows", wf) or {}
            stats["runs"] = int(stats.get("runs", 0)) + 1
            if retro.get("strategy_success"):
                stats["successes"] = int(stats.get("successes", 0)) + 1
            stats["success_rate"] = round(
                int(stats.get("successes", 0)) / stats["runs"], 3)
            self.brain.put("workflows", wf, stats)

        # Decision knowledge (lightweight; not the full ADR).
        if retro.get("decisions"):
            self.brain.append("decisions", {
                "workflow": wf, "agents": retro.get("agents_used", []),
                "risk_level": retro.get("risk_level"),
                "success": retro.get("strategy_success"),
            })

        # Failure knowledge (so future runs can warn).
        if int(retro.get("failures", 0)) > 0:
            self.brain.append("bugs", {
                "workflow": wf, "agents": retro.get("agents_used", []),
                "failures": retro.get("failures"), "retries": retro.get("retries"),
            })

        self.brain.append("history", {
            "event": "learned", "status": retro.get("status"),
            "workflow": wf, "success": retro.get("strategy_success"),
        })
        return self.brain.version()
