"""Project Evolution — structured knowledge enrichment after each execution."""
import os
import tempfile
import unittest
from pathlib import Path

from nx_knowledge.evolution.project_evolution import ProjectEvolutionEngine
from nx_knowledge.evolution.self_improvement import SelfImprovementEngine
from nx_knowledge.memory.brain import ProjectBrain
from nx_core.observability.events import EventBus


class _Home:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        cfg = Path(self.tmp.name) / ".ai-project-assistant"
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


_RETRO = {
    "request": "Fix OAuth token bug and add migration",
    "files_changed": [
        "apps/api/services/auth_service.py", "apps/api/routes.py",
        "libs/db/migrations/0002_tokens.sql", "tests/test_auth.py",
        ".github/workflows/ci.yml", "pyproject.toml", "apps/web/components/Login.tsx",
    ],
    "strategy_success": True, "failures": 0, "retries": 1, "workflow": "full-dev",
    "agents_used": ["backend", "database", "security", "qa"],
    "decisions": [{"workflow": "full-dev", "agents": ["backend", "database"], "risk_level": "high"}],
}


class TestClassification(unittest.TestCase):
    def test_all_categories_recorded(self):
        with _Home():
            b = ProjectBrain()
            b.put("architecture", "current", {"frameworks": ["FastAPI", "React"]})
            counts = ProjectEvolutionEngine(b).evolve(_RETRO)
            self.assertGreaterEqual(counts["services"], 1)
            self.assertGreaterEqual(counts["apis"], 1)
            self.assertGreaterEqual(counts["entities"], 1)
            self.assertGreaterEqual(counts["tests"], 1)
            self.assertGreaterEqual(counts["integrations"], 1)
            self.assertGreaterEqual(counts["dependencies"], 1)
            self.assertIn("apps", counts and b.get("modules"))

    def test_facets_populated(self):
        with _Home():
            b = ProjectBrain()
            b.put("architecture", "current", {"frameworks": ["FastAPI"]})
            ProjectEvolutionEngine(b).evolve(_RETRO)
            self.assertTrue(b.get("services"))
            self.assertTrue(b.get("apis"))
            self.assertTrue(b.get("database"))   # entities
            self.assertTrue(b.get("tests"))
            self.assertTrue(b.get("integrations"))
            self.assertTrue(b.get("dependencies"))
            self.assertIn("fastapi", b.get("patterns"))  # architectural pattern

    def test_modules_skip_dot_dirs(self):
        with _Home():
            b = ProjectBrain()
            ProjectEvolutionEngine(b).evolve(_RETRO)
            mods = b.get("modules")
            self.assertIn("apps", mods)
            self.assertIn("libs", mods)
            self.assertNotIn("github", mods)   # .github excluded

    def test_fixed_bug_recorded(self):
        with _Home():
            b = ProjectBrain()
            ProjectEvolutionEngine(b).evolve(_RETRO)
            bugs = b.read_log("bugs")
            self.assertTrue(any(r.get("status") == "fixed" for r in bugs))

    def test_lessons_and_decisions(self):
        with _Home():
            b = ProjectBrain()
            ProjectEvolutionEngine(b).evolve(_RETRO)
            self.assertTrue(b.read_log("lessons"))
            self.assertTrue(b.read_log("decisions"))

    def test_related_files_paths_only(self):
        with _Home():
            b = ProjectBrain()
            ProjectEvolutionEngine(b).evolve(_RETRO)
            rec = b.read_log("knowledge")[-1]
            self.assertEqual(rec["kind"], "evolution")
            self.assertIn("apps/api/routes.py", rec["related_files"])

    def test_impact_counts_accumulate(self):
        with _Home():
            b = ProjectBrain()
            eng = ProjectEvolutionEngine(b)
            eng.evolve(_RETRO)
            eng.evolve(_RETRO)
            svc = next(iter(b.get("services").values()))
            self.assertEqual(svc["impacted"], 2)


class TestNeverStoresCodeOrModelOutput(unittest.TestCase):
    def test_no_code_or_model_text_persisted(self):
        with _Home():
            b = ProjectBrain()
            retro = dict(_RETRO)
            # even if a model-output-like field sneaks in, it must not be stored
            retro["notes"] = "def hacked():\n    import os\n    return os.system('x')"
            ProjectEvolutionEngine(b).evolve(retro)
            import json
            blob = json.dumps([b.get("services"), b.read_log("knowledge"),
                               b.read_log("decisions"), b.read_log("lessons")])
            self.assertNotIn("def ", blob)
            self.assertNotIn("import os", blob)
            self.assertNotIn("os.system", blob)


class TestIntegrationWithLearning(unittest.TestCase):
    def test_self_improvement_runs_project_evolution(self):
        with _Home():
            bus = EventBus()
            si = SelfImprovementEngine(bus=bus)
            bus.emit("pipeline.started", {"request": "Add OAuth login"})
            bus.emit("decision.made", {"workflow": "full-dev", "agents": ["backend"], "risk_level": "high"})
            bus.emit("task.completed", {"agent": "backend"})
            bus.emit("review.completed", {"files": ["apps/api/services/auth.py", "tests/test_auth.py"]})
            bus.emit("run.completed", {"status": "done", "metrics": {}})
            bus.emit("delivery.completed", {"gates_passed": True})
            bus.emit("pipeline.completed", {"request": "Add OAuth login"})
            know = si.insights()["knowledge"]
            self.assertGreaterEqual(know["services"], 1)
            self.assertGreaterEqual(know["tests"], 1)


if __name__ == "__main__":
    unittest.main()
