"""Engineering Packs — catalog, install, Pack Provider, and the `nxai pack` CLI."""
import json
import os
import tempfile
import unittest
from pathlib import Path

import nx_packs
from nx_providers.knowledge.packs import PackProvider
from nx_cli import orchestrator

EXPECTED = {"lgpd", "security", "owasp", "ai", "cloud", "docker",
            "multi-tenant", "observability", "testing", "billing", "authentication"}


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
            packs_root = Path(tmp) / ".ai-project" / "packs"
            dst = nx_packs.install("lgpd", packs_root)
            self.assertTrue((dst / "pack.json").is_file())
            self.assertEqual(list(dst.rglob("*.py")), [])  # no code installed

            prov = PackProvider(root=Path(tmp) / ".ai-project")
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
            prov = PackProvider(root=Path(tmp) / ".ai-project")
            self.assertEqual(prov.index(), 0)
            self.assertEqual(prov.catalog(), [])


class TestPackCLI(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("AIES_HOME")
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / ".ai-project"
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


if __name__ == "__main__":
    unittest.main()
