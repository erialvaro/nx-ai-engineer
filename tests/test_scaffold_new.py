"""`nxai new` scaffolding + `nxai platform-audit`.

Proves the v2 scaffolding framework: the cloud-agnostic stack renders into a
real project (variables substituted, dotfiles materialized) and the generated
foundation passes the platform-readiness audit with zero failures.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nx_cli import bootstrap, orchestrator, platform_audit

_TOKEN = __import__("re").compile(r"\{\{\s*\w+\s*\}\}")


class TestScaffoldNew(unittest.TestCase):
    def _make(self, tmp: str, name: str = "my-platform"):
        return bootstrap.new_project(name, tmp, stack="cloud-agnostic")

    def test_renders_cloud_agnostic_foundation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, written, _ = self._make(tmp)
            self.assertEqual(root.name, "my-platform")
            self.assertGreater(written, 30)
            # core foundation files exist
            for rel in ("docker-compose.yml", "docker-compose.override.yml",
                        "docker-compose.prod.yml", "Makefile", "README.md",
                        "backend/app/main.py", "backend/app/db/adapter.py",
                        "backend/Dockerfile", "frontend/package.json",
                        "frontend/Dockerfile", "supabase/migrations/0001_init.sql"):
                self.assertTrue((root / rel).is_file(), f"missing {rel}")

    def test_dotfiles_materialized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, *_ = self._make(tmp)
            for dotfile in (".gitignore", ".env.example", ".editorconfig",
                            "backend/.dockerignore", "frontend/.dockerignore",
                            "logs/.gitkeep", "volumes/.gitkeep"):
                self.assertTrue((root / dotfile).is_file(), f"missing {dotfile}")
            # the dot. source names must NOT leak through
            self.assertFalse((root / "dot.gitignore").exists())

    def test_variables_substituted_and_no_tokens_left(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, *_ = self._make(tmp, name="Acme Store")
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("Acme Store", readme)                 # project_title
            pkg = (root / "frontend/package.json").read_text(encoding="utf-8")
            self.assertIn("acme-store-frontend", pkg)           # project_slug
            # no unresolved {{ token }} anywhere in the rendered tree
            leftovers = [str(p.relative_to(root)) for p in root.rglob("*")
                         if p.is_file() and _TOKEN.search(p.read_text(encoding="utf-8", errors="ignore"))]
            self.assertEqual(leftovers, [], f"unrendered tokens in {leftovers}")

    def test_generated_foundation_passes_platform_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, *_ = self._make(tmp)
            checks = platform_audit.audit(root)
            summary = platform_audit.summarize(checks)
            fails = [f"{c.dimension}/{c.name}: {c.detail}"
                     for c in checks if c.status == platform_audit.FAIL]
            self.assertTrue(summary["ok"], f"platform-audit FAILED: {fails}")
            # every dimension is represented
            dims = {c.dimension for c in checks}
            self.assertEqual(len(dims), 8, f"expected 8 dimensions, got {dims}")

    def test_unknown_stack_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                bootstrap.new_project("x", tmp, stack="does-not-exist")

    def test_refuses_nonempty_target_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "occupied").mkdir()
            (Path(tmp) / "occupied" / "keep.txt").write_text("x", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                bootstrap.new_project("occupied", tmp, stack="cloud-agnostic")

    def test_cli_registers_new_and_platform_audit(self):
        parser = orchestrator.build_parser()
        choices: set = set()
        for action in parser._actions:
            if getattr(action, "choices", None):
                choices |= set(action.choices)
        self.assertIn("new", choices)
        self.assertIn("platform-audit", choices)

    def test_available_stacks_lists_cloud_agnostic(self):
        self.assertIn("cloud-agnostic", bootstrap.available_stacks())


if __name__ == "__main__":
    unittest.main()
