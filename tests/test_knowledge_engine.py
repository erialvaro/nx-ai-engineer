"""Knowledge Engine — coordinates the three memories (Brain/Obsidian/Git)."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from nx_knowledge.knowledge.engine import KnowledgeEngine
from nx_knowledge.memory.brain import ProjectBrain
from nx_core.observability.events import EventBus


class _Repo:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = Path(self.tmp.name)
        (r / "src").mkdir()
        (r / "src/app.py").write_text("x=1\n", encoding="utf-8")
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.email=a@b.c", "-c", "user.name=t", "commit", "-qm", "init"]):
            subprocess.run(["git", *args], cwd=r, capture_output=True)
        (r / ".ai-project-assistant").mkdir()
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(r / ".ai-project-assistant")
        self.root = r
        return r

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        try:
            self.tmp.cleanup()
        except (PermissionError, OSError):
            pass


class TestAccessPoint(unittest.TestCase):
    def test_retrieve_delegates_to_providers(self):
        with _Repo():
            eng = KnowledgeEngine(ProjectBrain())
            hits = eng.retrieve({"query": "app"}, providers=["filesystem"])
            self.assertTrue(any("app.py" in h.ref for h in hits))

    def test_owns_registry_and_obsidian(self):
        with _Repo():
            eng = KnowledgeEngine(ProjectBrain())
            self.assertIn("filesystem", eng.registry.names())
            self.assertIsNotNone(eng.obsidian)


class TestThreeMemoriesSync(unittest.TestCase):
    def test_sync_reports_three_memories(self):
        with _Repo():
            brain = ProjectBrain()
            brain.put("services", "auth", {"path": "api/auth"})
            eng = KnowledgeEngine(brain)
            rep = eng.sync()
            self.assertEqual(rep["operational"]["memory"], "Project Brain")
            self.assertGreater(rep["organizational"]["notes"], 0)   # Obsidian written
            self.assertIsNotNone(rep["historical"]["head"])         # Git head present

    def test_status_synchronized_after_sync(self):
        with _Repo():
            brain = ProjectBrain()
            eng = KnowledgeEngine(brain)
            before = eng.status()
            self.assertFalse(before["synchronized"])   # nothing synced yet
            eng.sync()
            after = eng.status()
            self.assertTrue(after["organizational"]["in_sync"])
            self.assertEqual(after["organizational"]["brain_version"],
                             after["operational"]["version"])
            self.assertTrue(after["synchronized"])
            self.assertTrue(after["historical"]["is_repo"])

    def test_auto_sync_on_pipeline_completed(self):
        with _Repo():
            bus = EventBus()
            eng = KnowledgeEngine(ProjectBrain(), bus=bus)
            bus.emit("pipeline.completed", {"request": "x"})
            self.assertEqual(len(bus.history("knowledge.synced")), 1)
            self.assertTrue(eng.status()["synchronized"])

    def test_git_snapshot_commit_opt_in(self):
        with _Repo() as r:
            brain = ProjectBrain()
            brain.put("services", "auth", {"path": "api/auth"})
            eng = KnowledgeEngine(brain)
            before = eng.status()["historical"]["commits"]
            rep = eng.sync(commit=True)
            self.assertTrue(rep["historical"]["committed"])
            after = eng.status()["historical"]["commits"]
            self.assertEqual(after, before + 1)   # one historical snapshot commit


class TestContextFlowsThroughEngine(unittest.TestCase):
    def test_context_builder_uses_engine(self):
        with _Repo():
            from nx_core.kernel.domain import Subtask
            from nx_knowledge.memory.context import ContextBuilder
            eng = KnowledgeEngine(ProjectBrain())
            res = ContextBuilder(knowledge=eng).build(
                agent="backend",
                subtask=Subtask(id="backend", agent="backend",
                                objective="work on app", areas=["src"]),
                use_cache=False)
            self.assertIn("src/app.py", res.context.files)


if __name__ == "__main__":
    unittest.main()
