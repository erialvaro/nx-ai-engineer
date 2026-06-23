"""PR-5 — Project Brain, Learning, Experience and Semantic tests."""
import os
import tempfile
import unittest
from pathlib import Path

from nx_core.experience.metrics import ExperienceRecorder
from nx_knowledge.memory.brain import ProjectBrain, looks_like_code
from nx_knowledge.memory.learning import LearningEngine
from nx_knowledge.memory.semantic import Hit, NullSemanticIndex, SemanticIndex
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


class TestBrain(unittest.TestCase):
    def test_put_get_merge_and_version(self):
        with _Home():
            b = ProjectBrain()
            self.assertEqual(b.version(), 0)
            b.put("services", "auth", {"path": "api/auth", "kind": "service"})
            b.put("services", "auth", {"owner": "backend"})  # merge
            rec = b.get("services", "auth")
            self.assertEqual(rec["path"], "api/auth")
            self.assertEqual(rec["owner"], "backend")
            self.assertGreaterEqual(b.version(), 2)

    def test_append_log(self):
        with _Home():
            b = ProjectBrain()
            b.append("history", {"event": "x"})
            b.append("history", {"event": "y"})
            log = b.read_log("history")
            self.assertEqual(len(log), 2)
            self.assertTrue(all("ts" in r and "id" in r for r in log))

    def test_never_stores_code(self):
        with _Home():
            b = ProjectBrain()
            code = "def f():\n    import os\n    return os"
            b.put("patterns", "leak", {"note": "ok", "snippet": code})
            rec = b.get("patterns", "leak")
            self.assertIn("note", rec)
            self.assertNotIn("snippet", rec)  # code-like value dropped

    def test_looks_like_code(self):
        self.assertTrue(looks_like_code("import os\nclass A: pass"))
        self.assertFalse(looks_like_code("a short human note"))

    def test_migrate_legacy(self):
        with _Home() as cfg:
            from nx_core.foundation import util
            util.write_json(cfg / "memory" / "architecture.json",
                            {"frameworks": ["React"], "stacks": ["Node.js"], "is_monorepo": True})
            b = ProjectBrain()
            self.assertTrue(b.migrate_legacy())
            self.assertEqual(b.get("architecture", "current")["frameworks"], ["React"])
            self.assertIn("react", b.get("patterns"))


class TestLearning(unittest.TestCase):
    def test_run_completed_creates_retrospective(self):
        with _Home():
            bus = EventBus()
            le = LearningEngine(bus=bus)
            bus.emit("run.completed", {"run_id": "r1", "status": "done", "metrics": {"total": 3}})
            self.assertEqual(len(le.brain.read_log("retrospectives")), 1)
            self.assertEqual(len(bus.history("brain.updated")), 1)

    def test_review_and_delivery_recorded(self):
        with _Home():
            bus = EventBus()
            le = LearningEngine(bus=bus)
            bus.emit("review.completed", {"findings": 2, "without_tests": 1})
            bus.emit("delivery.completed", {"task": "t1", "rollback": "revert"})
            self.assertEqual(len(le.brain.read_log("knowledge")), 1)
            self.assertEqual(len(le.brain.read_log("decisions")), 1)


class TestExperience(unittest.TestCase):
    def test_aggregates_kpis(self):
        with _Home():
            bus = EventBus()
            exp = ExperienceRecorder(bus=bus)
            bus.emit("task.completed", {})
            bus.emit("task.completed", {})
            bus.emit("task.failed", {})
            bus.emit("task.retrying", {})
            bus.emit("context.built", {"estimated_reduction": 0.8})
            s = exp.summary()
            self.assertEqual(s["tasks_completed"], 2)
            self.assertEqual(s["tasks_failed"], 1)
            self.assertAlmostEqual(s["success_rate"], 2 / 3, places=3)
            self.assertEqual(s["avg_context_reduction"], 0.8)

    def test_persist_summary(self):
        with _Home():
            exp = ExperienceRecorder(bus=EventBus())
            p = exp.persist_summary()
            self.assertTrue(p.exists())


class TestSemantic(unittest.TestCase):
    def test_keyword_index_search(self):
        idx = NullSemanticIndex()
        idx.index("d1", "OAuth authentication and token storage", {"facet": "decisions"})
        idx.index("d2", "frontend button styling", {"facet": "patterns"})
        hits = idx.search("token authentication", k=3)
        self.assertTrue(hits)
        self.assertEqual(hits[0].doc_id, "d1")
        self.assertIsInstance(hits[0], Hit)

    def test_protocol(self):
        self.assertIsInstance(NullSemanticIndex(), SemanticIndex)


if __name__ == "__main__":
    unittest.main()
