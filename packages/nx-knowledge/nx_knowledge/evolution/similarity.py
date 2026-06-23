"""Similar Task Detection — finds past tasks similar to a new request.

Reuses the Semantic Knowledge layer (`NullSemanticIndex`, keyword/Jaccard today;
a vector index can be swapped in via the SDK). The index is (re)built from the
Brain's retrospectives, so similarity improves as the platform learns.
"""
from __future__ import annotations

from typing import Optional

from ..memory.brain import ProjectBrain
from ..memory.semantic import Hit, NullSemanticIndex, SemanticIndex


class SimilarTaskDetector:
    name = "similar-task-detection"

    def __init__(self, *, index: Optional[SemanticIndex] = None) -> None:
        self.index = index or NullSemanticIndex()

    def index_past(self, brain: ProjectBrain | None = None) -> int:
        brain = brain or ProjectBrain()
        n = 0
        for r in brain.read_log("retrospectives"):
            req = r.get("request")
            if not req:
                continue
            self.index.index(r.get("id", req[:24]), req, {
                "agents": r.get("agents_used", []),
                "workflow": r.get("workflow"),
                "status": r.get("status"),
                "strategy_success": r.get("strategy_success"),
            })
            n += 1
        return n

    def find_similar(self, request: str, k: int = 3,
                     brain: ProjectBrain | None = None) -> list[Hit]:
        # Rebuild from the Brain so cross-run history is always considered.
        self.index_past(brain)
        return self.index.search(request, k=k)
