"""Prompt-4 — Autonomous Learning: the 7 evolution engines + integration."""
import os
import tempfile
import unittest
from pathlib import Path

from nx_knowledge.evolution import (
    BrainOptimizer, ExperienceAnalyzer, KnowledgeEvolution, PatternDiscovery,
    RecommendationEngine, SelfImprovementEngine, SimilarTaskDetector,
)
from nx_knowledge.memory.brain import ProjectBrain
from nx_core.observability.events import EventBus


class _Home:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        cfg = Path(self.tmp.name) / ".ai-project"
        cfg.mkdir()
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(cfg)
        return cfg

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        self.tmp.cleanup()


def _retro(req="Implement OAuth", agents=("backend", "database", "security"),
           failures=0, retries=1, wf="full-dev", success=True, risk="high"):
    return {"request": req, "duration_sec": 12.0, "status": "done" if success else "stuck",
            "agents_used": list(agents), "files_changed": ["apps/api/auth.py"],
            "failures": failures, "retries": retries, "workflow": wf,
            "strategy": "rule-based", "strategy_success": success, "risk_level": risk,
            "decisions": [{"workflow": wf, "agents": list(agents)}]}


class TestKnowledgeEvolution(unittest.TestCase):
    def test_evolve_records_and_updates_workflow_stats(self):
        with _Home():
            b = ProjectBrain()
            ke = KnowledgeEvolution(b)
            ke.evolve(_retro())
            ke.evolve(_retro(success=False))
            self.assertEqual(len(b.read_log("retrospectives")), 2)
            stats = b.get("workflows", "full-dev")
            self.assertEqual(stats["runs"], 2)
            self.assertEqual(stats["successes"], 1)
            self.assertEqual(stats["success_rate"], 0.5)

    def test_never_stores_code(self):
        with _Home():
            b = ProjectBrain()
            KnowledgeEvolution(b).evolve({**_retro(), "snippet": "def f():\n import os\n return os"})
            rec = b.read_log("retrospectives")[-1]
            self.assertNotIn("snippet", rec)


class TestExperienceAnalyzer(unittest.TestCase):
    def test_aggregates(self):
        with _Home():
            b = ProjectBrain()
            ke = KnowledgeEvolution(b)
            ke.evolve(_retro(retries=2))
            ke.evolve(_retro(success=False, failures=1))
            ins = ExperienceAnalyzer().analyze(b)
            self.assertEqual(ins["runs"], 2)
            self.assertEqual(ins["success_rate"], 0.5)
            self.assertGreater(ins["rework_rate"], 0)
            self.assertIn("backend", ins["agent_frequency"])


class TestPatternDiscovery(unittest.TestCase):
    def test_recurring_agent_sets(self):
        with _Home():
            b = ProjectBrain()
            ke = KnowledgeEvolution(b)
            for _ in range(3):
                ke.evolve(_retro())
            found = PatternDiscovery().persist(b)
            self.assertEqual(found["agent_sets"][0]["count"], 3)
            self.assertTrue(b.get("patterns", "recurring-agent-sets"))

    def test_failure_prone(self):
        with _Home():
            b = ProjectBrain()
            KnowledgeEvolution(b).evolve(_retro(failures=2))
            found = PatternDiscovery().discover(b.read_log("retrospectives"))
            self.assertTrue(found["failure_prone"])


class TestSimilarity(unittest.TestCase):
    def test_finds_similar_past_task(self):
        with _Home():
            b = ProjectBrain()
            KnowledgeEvolution(b).evolve(_retro(req="Implement OAuth login with tokens"))
            det = SimilarTaskDetector()
            hits = det.find_similar("Add OAuth token refresh", k=3, brain=b)
            self.assertTrue(hits)
            self.assertIn("full-dev", [h.meta.get("workflow") for h in hits])


class TestRecommendation(unittest.TestCase):
    def test_recommends_from_history(self):
        with _Home():
            b = ProjectBrain()
            ke = KnowledgeEvolution(b)
            for _ in range(2):
                ke.evolve(_retro(req="Implement OAuth login"))
            rec = RecommendationEngine(b).recommend("Add OAuth token endpoint")
            self.assertEqual(rec["recommended_workflow"], "full-dev")
            self.assertIn("backend", rec["recommended_agents"])


class TestBrainOptimizer(unittest.TestCase):
    def test_trims_logs(self):
        with _Home():
            b = ProjectBrain()
            for i in range(10):
                b.append("history", {"i": i})
            report = BrainOptimizer(b, caps={"history": 4}).optimize()
            self.assertEqual(report["trimmed"]["history"], 6)
            self.assertEqual(len(b.read_log("history")), 4)


class TestSelfImprovementEngine(unittest.TestCase):
    def _emit_run(self, bus, req="Implement OAuth login with tokens", success=True):
        bus.emit("pipeline.started", {"request": req})
        bus.emit("decision.made", {"workflow": "full-dev",
                                   "agents": ["backend", "database", "security"],
                                   "risk_level": "high", "parallelism": 3})
        for a in ["database", "security", "backend"]:
            bus.emit("task.completed", {"agent": a})
        bus.emit("task.retrying", {"attempt": 1})
        bus.emit("review.completed", {"findings": 1, "files": ["apps/api/auth.py"]})
        bus.emit("run.completed", {"status": "done" if success else "stuck", "metrics": {}})
        bus.emit("delivery.completed", {"gates_passed": success})
        bus.emit("pipeline.completed", {"request": req})

    def test_learns_after_run(self):
        with _Home():
            bus = EventBus()
            si = SelfImprovementEngine(bus=bus)
            self._emit_run(bus)
            self.assertEqual(len(bus.history("improvement.learned")), 1)
            ins = si.insights()
            self.assertEqual(ins["experience"]["runs"], 1)
            self.assertEqual(ins["experience"]["agent_frequency"]["backend"], 1)
            # rework captured (1 retry over 3 agents)
            self.assertGreater(ins["experience"]["rework_rate"], 0)

    def test_captures_required_signals(self):
        with _Home():
            bus = EventBus()
            si = SelfImprovementEngine(bus=bus)
            self._emit_run(bus)
            retro = si.brain.read_log("retrospectives")[-1]
            for key in ("duration_sec", "failures", "retries", "agents_used",
                        "files_changed", "decisions", "workflow", "strategy_success"):
                self.assertIn(key, retro)
            self.assertEqual(sorted(retro["agents_used"]), ["backend", "database", "security"])
            self.assertEqual(retro["files_changed"], ["apps/api/auth.py"])
            self.assertTrue(retro["strategy_success"])

    def test_recommendations_improve_with_history(self):
        with _Home():
            bus = EventBus()
            si = SelfImprovementEngine(bus=bus)
            self._emit_run(bus)
            rec = si.recommendations("Add OAuth refresh token")
            self.assertEqual(rec["recommended_workflow"], "full-dev")
            self.assertTrue(rec["similar_tasks"])


if __name__ == "__main__":
    unittest.main()
