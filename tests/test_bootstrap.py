"""nxai init/update bootstrap + the new CLI commands (version/doctor/docs/init/update)."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from nx_cli import bootstrap, orchestrator


class TestBootstrap(unittest.TestCase):
    def test_init_scaffolds_data_only_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, copied, _ = bootstrap.init(tmp)
            self.assertTrue(root.name == ".ai-project-assistant")
            # template assets laid down
            self.assertTrue((root / "agents").is_dir())
            self.assertTrue((root / "PROJECT_RULES.md").exists())
            self.assertTrue((root / "config.json").exists())
            self.assertTrue((root / "config.example.json").exists())
            # data dirs scaffolded (empty)
            for d in bootstrap.DATA_DIRS:
                self.assertTrue((root / d).is_dir(), f"{d} not scaffolded")
            # NO platform code copied into the project (.py engine files)
            self.assertEqual(list(root.rglob("orchestrator.py")), [])
            self.assertGreater(copied, 0)

    def test_init_is_idempotent_and_preserves_user_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, _ = bootstrap.init(tmp)
            (root / "config.json").write_text('{"project_name":"mine"}', encoding="utf-8")
            (root / "brain").mkdir(exist_ok=True)
            (root / "brain" / "keep.json").write_text("{}", encoding="utf-8")
            # second init must not clobber config or data
            bootstrap.init(tmp)
            self.assertIn("mine", (root / "config.json").read_text(encoding="utf-8"))
            self.assertTrue((root / "brain" / "keep.json").exists())

    def test_update_refreshes_template_but_not_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _, _ = bootstrap.init(tmp)
            cfg = root / "config.json"
            cfg.write_text('{"project_name":"mine"}', encoding="utf-8")
            (root / "brain" / "x.json").parent.mkdir(exist_ok=True)
            (root / "brain" / "x.json").write_text("{}", encoding="utf-8")
            # corrupt a template file; update must restore it
            (root / "PROJECT_RULES.md").write_text("STALE", encoding="utf-8")
            bootstrap.update(tmp)
            self.assertNotEqual((root / "PROJECT_RULES.md").read_text(encoding="utf-8"), "STALE")
            self.assertIn("mine", cfg.read_text(encoding="utf-8"))   # config preserved
            self.assertTrue((root / "brain" / "x.json").exists())     # data preserved

    def test_update_requires_existing_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                bootstrap.update(tmp)


class TestNewCommands(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("AIES_HOME")

    def tearDown(self):
        if self._home is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._home

    def test_parser_registers_new_commands(self):
        p = orchestrator.build_parser()
        for cmd in ("init", "update", "doctor", "docs", "version", "execute"):
            args = p.parse_args([cmd] if cmd not in ("init", "update", "execute")
                                else ([cmd, "x"] if cmd == "execute" else [cmd]))
            self.assertTrue(hasattr(args, "fn"))
        # execute routes to the pipeline handler
        self.assertEqual(p.parse_args(["execute", "g"]).fn.__name__, "cmd_pipeline")

    def test_version_and_docs_run(self):
        self.assertEqual(orchestrator.cmd_version(None), 0)
        ns = orchestrator.build_parser().parse_args(["docs"])
        self.assertEqual(orchestrator.cmd_docs(ns), 0)
        ns2 = orchestrator.build_parser().parse_args(["docs", "SDK_GUIDE"])
        self.assertEqual(orchestrator.cmd_docs(ns2), 0)

    def test_init_via_cli_scaffold_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = orchestrator.main(["init", tmp, "--no-audit"])
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmp) / ".ai-project-assistant" / "config.json").exists())

    def test_doctor_runs(self):
        ns = orchestrator.build_parser().parse_args(["doctor"])
        self.assertIn(orchestrator.cmd_doctor(ns), (0, 1))


if __name__ == "__main__":
    unittest.main()
