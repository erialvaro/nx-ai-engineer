"""Brain Optimizer — keeps the Project Brain compact and healthy.

Bounds the append-only logs (history/retrospectives/decisions/bugs) to their most
recent records so the Brain doesn't grow without limit, and reports what it did.
Pure maintenance; it never deletes knowledge facets, only caps log tails.
"""
from __future__ import annotations

from typing import Any

from ..memory.brain import ProjectBrain

# How many recent records to keep per append-only facet.
_CAPS = {"history": 500, "retrospectives": 300, "decisions": 300, "bugs": 200,
         "knowledge": 300}


class BrainOptimizer:
    name = "brain-optimizer"

    def __init__(self, brain: ProjectBrain | None = None, *, caps: dict | None = None) -> None:
        self.brain = brain or ProjectBrain()
        self._caps = {**_CAPS, **(caps or {})}

    def optimize(self) -> dict[str, Any]:
        trimmed: dict[str, int] = {}
        for facet, keep in self._caps.items():
            try:
                dropped = self.brain.trim_log(facet, keep)
                if dropped:
                    trimmed[facet] = dropped
            except Exception:
                pass
        return {"trimmed": trimmed, "version": self.brain.version()}
