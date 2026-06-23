"""Learning Engine — turns execution events into reusable knowledge.

Subscribes to run/review/delivery events and records retrospectives, used
agents, dependencies, timing and outcomes into the Project Brain. It stores
**knowledge, never code**, and bumps the Brain version on each update.
"""
from __future__ import annotations

from .brain import ProjectBrain


class LearningEngine:
    def __init__(self, brain: ProjectBrain | None = None, *, bus=None) -> None:
        self.brain = brain or ProjectBrain()
        if bus is not None:
            self.attach(bus)

    def attach(self, bus) -> None:
        bus.subscribe("run.completed", self._on_run)
        bus.subscribe("review.completed", self._on_review)
        bus.subscribe("delivery.completed", self._on_delivery)
        self._bus = bus

    # -- handlers --------------------------------------------------------- #
    def _on_run(self, event) -> None:
        p = event.payload or {}
        self.brain.append("retrospectives", {
            "kind": "run", "run_id": p.get("run_id"), "status": p.get("status"),
            "metrics": p.get("metrics", {}),
        })
        self.brain.append("history", {"event": "run.completed", "run_id": p.get("run_id"),
                                      "status": p.get("status")})
        self._emit_updated("run")

    def _on_review(self, event) -> None:
        p = event.payload or {}
        self.brain.append("knowledge", {
            "kind": "review", "findings": p.get("findings", 0),
            "without_tests": p.get("without_tests", 0),
            "critical": p.get("critical", 0),
        })
        self._emit_updated("review")

    def _on_delivery(self, event) -> None:
        p = event.payload or {}
        self.brain.append("decisions", {
            "kind": "delivery", "task": p.get("task"), "rollback": p.get("rollback"),
        })
        self._emit_updated("delivery")

    def _emit_updated(self, source: str) -> None:
        bus = getattr(self, "_bus", None)
        if bus is not None:
            bus.emit("brain.updated", {"source": source, "version": self.brain.version()})
