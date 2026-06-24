"""Engineering Packs — catalog, install, Pack Provider, and the `nxai pack` CLI."""
import json
import os
import tempfile
import unittest
from pathlib import Path

import nx_packs
from nx_providers.knowledge.packs import PackProvider
from nx_cli import orchestrator

EXPECTED = {"lgpd", "security", "owasp", "ai", "cloud", "docker", "multi-tenant",
            "observability", "testing", "billing", "authentication", "repo-standards"}


class TestCatalog(unittest.TestCase):
    def test_catalog_has_all_packs_well_formed(self):
        names = set(nx_packs.names())
        self.assertTrue(EXPECTED <= names, f"missing packs: {EXPECTED - names}")
        for name in nx_packs.names():
            d = nx_packs.pack_dir(name)
            for req in nx_packs.REQUIRED:
                self.assertTrue((d / req).is_file(), f"{name} missing {req}")
            m = nx_packs.manifest(name)
            for k in ("name", "title", "domain", "summary", "status"):
                self.assertIn(k, m)

    def test_reference_packs_are_stable(self):
        self.assertEqual(nx_packs.manifest("lgpd")["status"], "stable")
        self.assertEqual(nx_packs.manifest("security")["status"], "stable")

    def test_packs_contain_no_python_code(self):
        # Doctrine: packs are knowledge, never code.
        for name in nx_packs.names():
            self.assertEqual(list(nx_packs.pack_dir(name).rglob("*.py")), [],
                             f"{name} must not contain .py code")

    def test_unknown_pack_raises(self):
        with self.assertRaises(KeyError):
            nx_packs.pack_dir("does-not-exist")


class TestInstallAndProvider(unittest.TestCase):
    def test_install_then_provider_catalogs_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            packs_root = Path(tmp) / ".ai-project-assistant" / "packs"
            dst = nx_packs.install("lgpd", packs_root)
            self.assertTrue((dst / "pack.json").is_file())
            self.assertEqual(list(dst.rglob("*.py")), [])  # no code installed

            prov = PackProvider(root=Path(tmp) / ".ai-project-assistant")
            self.assertEqual(prov.index(), 1)
            items = prov.catalog()
            self.assertEqual(items[0].kind, "pack")
            self.assertEqual(items[0].metadata["name"], "lgpd")
            self.assertTrue(items[0].metadata["policies"])      # policies surfaced
            self.assertTrue(items[0].metadata["checklists"])    # checklists surfaced
            # retrievable by domain query
            hits = prov.retrieve({"query": "privacy pii consent"})
            self.assertTrue(any(h.metadata["name"] == "lgpd" for h in hits))

    def test_provider_empty_when_no_packs(self):
        with tempfile.TemporaryDirectory() as tmp:
            prov = PackProvider(root=Path(tmp) / ".ai-project-assistant")
            self.assertEqual(prov.index(), 0)
            self.assertEqual(prov.catalog(), [])


class TestPackCLI(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("AIES_HOME")
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / ".ai-project-assistant"
        root.mkdir()
        os.environ["AIES_HOME"] = str(root)

    def tearDown(self):
        if self._home is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._home
        self.tmp.cleanup()

    def test_pack_list_add_remove(self):
        self.assertEqual(orchestrator.main(["pack", "list"]), 0)
        self.assertEqual(orchestrator.main(["pack", "add", "security"]), 0)
        installed = Path(os.environ["AIES_HOME"]) / "packs" / "security" / "pack.json"
        self.assertTrue(installed.is_file())
        self.assertEqual(orchestrator.main(["pack", "show", "security"]), 0)
        self.assertEqual(orchestrator.main(["pack", "remove", "security"]), 0)
        self.assertFalse(installed.parent.is_dir())

    def test_pack_add_unknown_fails(self):
        self.assertEqual(orchestrator.main(["pack", "add", "nope"]), 2)


class TestScaffold(unittest.TestCase):
    def test_scaffold_lays_repo_standards(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = orchestrator.main(["scaffold", "--stack", "python", "--path", tmp])
            self.assertEqual(rc, 0)
            root = Path(tmp)
            for f in ("CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md",
                      ".editorconfig", ".gitignore",
                      ".github/PULL_REQUEST_TEMPLATE.md",
                      ".github/ISSUE_TEMPLATE/bug_report.md",
                      ".github/workflows/ci.yml"):
                self.assertTrue((root / f).exists(), f"missing {f}")
            # the python CI variant was chosen
            self.assertIn("setup-python", (root / ".github/workflows/ci.yml").read_text(encoding="utf-8"))

    def test_scaffold_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            orchestrator.main(["scaffold", "--stack", "go", "--path", tmp])
            (Path(tmp) / "CONTRIBUTING.md").write_text("MINE", encoding="utf-8")
            orchestrator.main(["scaffold", "--stack", "go", "--path", tmp])  # no --force
            self.assertEqual((Path(tmp) / "CONTRIBUTING.md").read_text(encoding="utf-8"), "MINE")

    def test_scaffold_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            orchestrator.main(["scaffold", "--stack", "node", "--dry-run", "--path", tmp])
            self.assertFalse((Path(tmp) / "CONTRIBUTING.md").exists())


if __name__ == "__main__":
    unittest.main()
