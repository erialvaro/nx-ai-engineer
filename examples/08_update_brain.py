"""Example 8 — Update the Project Brain (knowledge, never code).

Shows the Brain API directly and the autonomous-learning path. Run:
    python examples/08_update_brain.py
"""
from _bootstrap import aies_home  # noqa: F401

from nx_knowledge.evolution import SelfImprovementEngine
from nx_knowledge.memory.brain import ProjectBrain
from nx_core.observability.events import EventBus

if __name__ == "__main__":
    brain = ProjectBrain()

    # --- direct API: key/value + append-only facets ---
    brain.put("services", "auth", {"path": "api/auth", "owner": "backend"})
    brain.append("history", {"event": "manual-note", "detail": "seeded auth service"})
    print("services/auth:", brain.get("services", "auth"))
    print("brain version:", brain.version())

    # The code guard drops code-like values automatically:
    brain.put("patterns", "leak", {"note": "ok", "snippet": "def f():\n import os"})
    print("code stored?:", "snippet" in brain.get("patterns", "leak"))  # -> False

    # --- autonomous path: learn from a (simulated) pipeline run ---
    bus = EventBus()
    si = SelfImprovementEngine(brain, bus=bus)
    bus.emit("pipeline.started", {"request": "Add OAuth login"})
    bus.emit("decision.made", {"workflow": "full-dev",
                               "agents": ["backend", "database"], "risk_level": "high"})
    bus.emit("task.completed", {"agent": "backend"})
    bus.emit("task.completed", {"agent": "database"})
    bus.emit("run.completed", {"status": "done", "metrics": {}})
    bus.emit("delivery.completed", {"gates_passed": True})
    bus.emit("pipeline.completed", {"request": "Add OAuth login"})

    print("learned runs:", si.insights()["experience"]["runs"])
    print("recommendation:", si.recommendations("Add OAuth logout")["recommended_workflow"])
