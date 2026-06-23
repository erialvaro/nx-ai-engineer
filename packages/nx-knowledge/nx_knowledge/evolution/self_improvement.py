"""Self Improvement Engine — makes AIES learn from every execution.

It subscribes to the event bus and, per pipeline run, accumulates the signals the
platform must learn — **time, failures, rework, agents used, files changed,
decisions, strategy success** — then, on `pipeline.completed`, assembles a
retrospective and drives Knowledge Evolution, Pattern Discovery, Similar-Task
indexing and (periodically) Brain optimization. It stores **knowledge, never
code** (file paths are metadata; the Brain's code guard still applies).

Reuses ProjectBrain, the Semantic index and the Experience layer — no new
persistence is invented.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from ..memory.brain import ProjectBrain
from .brain_optimizer import BrainOptimizer
from .experience_analyzer import ExperienceAnalyzer
from .knowledge_evolution import KnowledgeEvolution
from .pattern_discovery import PatternDiscovery
from .project_evolution import ProjectEvolutionEngine
from .recommendation import RecommendationEngine
from .similarity import SimilarTaskDetector


def _parse_ts(ts: str | None) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        return None


class SelfImprovementEngine:
    name = "self-improvement"

    def __init__(self, brain: Optional[ProjectBrain] = None, *, bus=None,
                 optimize_every: int = 20) -> None:
        self.brain = brain or ProjectBrain()
        self.evolution = KnowledgeEvolution(self.brain)
        self.project_evolution = ProjectEvolutionEngine(self.brain)
        self.patterns = PatternDiscovery()
        self.optimizer = BrainOptimizer(self.brain)
        self.analyzer = ExperienceAnalyzer()
        self.similarity = SimilarTaskDetector()
        self._optimize_every = optimize_every
        self._runs_since_opt = 0
        self._bus = None
        self._reset()
        if bus is not None:
            self.attach(bus)

    # -- wiring ----------------------------------------------------------- #
    def attach(self, bus) -> None:
        self._bus = bus
        bus.subscribe("pipeline.started", self._on_start)
        bus.subscribe("decision.made", self._on_decision)
        bus.subscribe("task.completed", self._on_task_done)
        bus.subscribe("task.failed", self._on_fail)
        bus.subscribe("task.retrying", self._on_retry)
        bus.subscribe("review.completed", self._on_review)
        bus.subscribe("run.completed", self._on_run_completed)
        bus.subscribe("delivery.completed", self._on_delivery)
        bus.subscribe("pipeline.completed", self._on_complete)

    def _reset(self) -> None:
        self._cur: dict[str, Any] = {
            "request": "", "agents": set(), "files": [], "failures": 0,
            "retries": 0, "status": "unknown", "workflow": None,
            "risk_level": None, "decisions": [], "success": None,
        }
        self._start_ts: Optional[str] = None

    # -- event handlers (accumulate per-run signals) --------------------- #
    def _on_start(self, e) -> None:
        self._reset()
        self._start_ts = e.ts
        self._cur["request"] = (e.payload or {}).get("request", "")

    def _on_decision(self, e) -> None:
        p = e.payload or {}
        self._cur["workflow"] = p.get("workflow")
        self._cur["risk_level"] = p.get("risk_level")
        self._cur["decisions"].append({
            "workflow": p.get("workflow"), "agents": p.get("agents"),
            "risk_level": p.get("risk_level"), "parallelism": p.get("parallelism"),
        })

    def _on_task_done(self, e) -> None:
        agent = (e.payload or {}).get("agent")
        if agent:
            self._cur["agents"].add(agent)

    def _on_fail(self, e) -> None:
        self._cur["failures"] += 1

    def _on_retry(self, e) -> None:
        self._cur["retries"] += 1

    def _on_review(self, e) -> None:
        files = (e.payload or {}).get("files")
        if files:
            self._cur["files"] = list(files)

    def _on_run_completed(self, e) -> None:
        self._cur["status"] = (e.payload or {}).get("status", self._cur["status"])

    def _on_delivery(self, e) -> None:
        gates = (e.payload or {}).get("gates_passed", True)
        self._cur["success"] = bool(gates) and self._cur.get("status") == "done"

    def _on_complete(self, e) -> None:
        retro = self._build_retro(end_ts=e.ts)
        self.learn(retro)
        self._reset()

    # -- the learning step ----------------------------------------------- #
    def _build_retro(self, end_ts: str | None = None) -> dict[str, Any]:
        cur = self._cur
        start, end = _parse_ts(self._start_ts), _parse_ts(end_ts)
        duration = (end - start).total_seconds() if (start and end) else None
        success = cur["success"]
        if success is None:
            success = cur.get("status") == "done"
        return {
            "request": (cur["request"] or "")[:200],
            "duration_sec": duration,
            "status": cur["status"],
            "agents_used": sorted(cur["agents"]),
            "files_changed": cur["files"][:50],
            "failures": cur["failures"],
            "retries": cur["retries"],            # rework
            "workflow": cur["workflow"],
            "strategy": "rule-based",
            "strategy_success": bool(success),
            "risk_level": cur["risk_level"],
            "decisions": cur["decisions"],
        }

    def learn(self, retro: dict[str, Any]) -> dict[str, Any]:
        """Consolidate a retrospective into the Brain and evolve knowledge."""
        version = self.evolution.evolve(retro)
        # Enrich structured project knowledge (modules/services/apis/entities/
        # tests/integrations/dependencies/patterns/bugs/decisions/lessons/files).
        try:
            self.project_evolution.evolve(retro)
        except Exception as exc:
            if self._bus is not None:
                self._bus.emit("evolution.error", {"error": repr(exc)})
        self.patterns.persist(self.brain)
        self.similarity.index_past(self.brain)

        self._runs_since_opt += 1
        opt = None
        if self._runs_since_opt >= self._optimize_every:
            opt = self.optimizer.optimize()
            self._runs_since_opt = 0

        if self._bus is not None:
            self._bus.emit("improvement.learned", {
                "status": retro["status"], "workflow": retro["workflow"],
                "agents": retro["agents_used"], "success": retro["strategy_success"],
                "brain_version": version,
            })
            self._bus.emit("brain.updated", {"source": "self-improvement", "version": version})
        return {"version": version, "optimized": opt}

    # -- query surface ---------------------------------------------------- #
    def recommendations(self, request: str) -> dict[str, Any]:
        return RecommendationEngine(self.brain, similarity=self.similarity,
                                    analyzer=self.analyzer).recommend(request)

    def insights(self) -> dict[str, Any]:
        return {"experience": self.analyzer.analyze(self.brain),
                "patterns": {
                    "recurring_agent_sets": self.brain.get("patterns", "recurring-agent-sets"),
                    "failure_prone": self.brain.get("patterns", "failure-prone-agents"),
                    "hot_areas": self.brain.get("patterns", "hot-areas"),
                },
                "knowledge": self.project_evolution.summary(),
                "brain_version": self.brain.version()}
