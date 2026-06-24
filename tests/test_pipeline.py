"""PR-7 — end-to-end Pipeline tests (run in a throwaway git project)."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from nx_core.kernel.engine import ExecutionMode
from nx_runtime.kernel.pipeline import Pipeline
from nx_workflow.workflow import default_registry


class _Project:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "apps" / "api" / "services").mkdir(parents=True)
        (root / "tests").mkdir()
        (root / "apps/api/services/auth_service.py").write_text("x=1\n", encoding="utf-8")
        (root / "tests/test_auth.py").write_text("def t():pass\n", encoding="utf-8")
        (root / "pyproject.toml").write_text("[project]\nname='d'\n", encoding="utf-8")
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.email=a@b.c", "-c", "user.name=t", "commit", "-qm", "i"]):
            subprocess.run(["git", *args], cwd=root, capture_output=True)
        (root / ".ai-project-assistant").mkdir()
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(root / ".ai-project-assistant")
        return root

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        try:
            self.tmp.cleanup()
        except (PermissionError, OSError):
            pass


class TestPipeline(unittest.TestCase):
    def test_full_dev_workflow_registered(self):
        self.assertIn("full-dev", default_registry().names())

    def test_dry_run_end_to_end(self):
        with _Project():
            res = Pipeline().run("Implement OAuth login with tokens", mode=ExecutionMode.DRY_RUN)
            self.assertTrue(res.selected_agents)
            self.assertIn("security", res.selected_agents)
            self.assertNotIn("frontend", res.selected_agents)
            self.assertEqual(res.execution["status"], "done")
            self.assertIn("total", res.execution["metrics"])

    def test_execute_runs_full_cycle_and_delivers(self):
        with _Project():
            res = Pipeline().run("Implement OAuth login with tokens", mode=ExecutionMode.EXECUTE)
            self.assertEqual(res.execution["status"], "done")
            self.assertTrue(res.delivery)  # delivery ran on execute
            self.assertGreaterEqual(res.brain_version, 1)  # learning updated brain
            self.assertIn("success_rate", res.experience)

    def test_pipeline_emits_lifecycle_events(self):
        with _Project():
            from nx_core.observability.events import EventBus
            bus = EventBus()
            Pipeline(bus=bus).run("Add a small util", mode=ExecutionMode.DRY_RUN)
            kinds = {e.type for e in bus.history()}
            self.assertTrue({"pipeline.started", "pipeline.completed", "run.completed",
                             "agent.selected", "review.completed"} <= kinds)

    def test_experience_persisted(self):
        with _Project() as root:
            Pipeline().run("Add a small util", mode=ExecutionMode.DRY_RUN)
            self.assertTrue((root / ".ai-project-assistant" / "experience" / "summary.json").exists())


if __name__ == "__main__":
    unittest.main()
