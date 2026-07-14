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
            "observability", "testing", "billing", "authentication", "repo-standards",
            "postgres", "mongodb", "seo", "copywriter", "design"}


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

    def test_seo_pack_and_agent(self):
        m = nx_packs.manifest("seo")
        self.assertEqual(m["category"], "seo")
        self.assertEqual(m["status"], "stable")
        self.assertIn("seo", m["applies_to"])
        d = nx_packs.pack_dir("seo")
        for f in ("structured-data.md", "ai-discoverability.md", "performance.md",
                  "anti-patterns.md", "prompts/specialist.md", "templates/audit.md",
                  "templates/report.md"):
            self.assertTrue((d / f).is_file(), f"seo pack missing {f}")
        # the PageSpeed Insights reporting workflow is baked into the pack
        self.assertIn("pagespeed.web.dev", (d / "performance.md").read_text(encoding="utf-8"))
        # the executor agent is registered, ordered, and owns SEO-dedicated files
        from nx_core import agents
        reg = agents.registry()
        self.assertIn("seo", reg)
        self.assertIn("seo", agents.CANON_ORDER)
        self.assertTrue(reg["seo"].owns("app/robots.txt"))       # SEO-dedicated file
        self.assertFalse(reg["seo"].owns("app/api/users.ts"))    # forbidden (backend)

    def test_copywriter_pack_and_agent(self):
        m = nx_packs.manifest("copywriter")
        self.assertEqual(m["category"], "content")
        self.assertEqual(m["status"], "stable")
        self.assertIn("copywriter", m["applies_to"])
        d = nx_packs.pack_dir("copywriter")
        for f in ("anti-patterns.md", "voice-and-tone.md", "frameworks.md",
                  "tech-domain.md", "seo-writing.md", "prompts/specialist.md",
                  "templates/brief.md"):
            self.assertTrue((d / f).is_file(), f"copywriter pack missing {f}")
        # the seo pack now also feeds the copywriter agent
        self.assertIn("copywriter", nx_packs.manifest("seo")["applies_to"])
        # the agent is registered, ordered, and owns content copy (not code)
        from nx_core import agents
        reg = agents.registry()
        self.assertIn("copywriter", reg)
        self.assertIn("copywriter", agents.CANON_ORDER)
        self.assertTrue(reg["copywriter"].owns("content/blog/post.mdx"))
        self.assertFalse(reg["copywriter"].owns("web/App.tsx"))       # forbidden (frontend)

    def test_design_pack_and_designer_agent(self):
        m = nx_packs.manifest("design")
        self.assertEqual(m["category"], "design")
        self.assertEqual(m["status"], "stable")
        self.assertIn("designer", m["applies_to"])
        d = nx_packs.pack_dir("design")
        for f in ("design-system.md", "typography.md", "color.md", "layout-spacing.md",
                  "accessibility.md", "motion.md", "tooling.md", "anti-patterns.md",
                  "prompts/specialist.md", "templates/design-brief.md"):
            self.assertTrue((d / f).is_file(), f"design pack missing {f}")
        # the tooling the agent must use is documented
        tooling = (d / "tooling.md").read_text(encoding="utf-8")
        for tool in ("ui-ux-pro-max", "21st-cli-use", "21st-ai", "21st-registry",
                     "21st-design-sync", "dataviz", "framer-motion"):
            self.assertIn(tool, tooling, f"tooling.md must document {tool}")
        # design moves Core Web Vitals -> the seo pack also feeds the designer
        self.assertIn("designer", nx_packs.manifest("seo")["applies_to"])
        # the agent is registered, runs BEFORE frontend, and owns the design system
        from nx_core import agents
        reg = agents.registry()
        self.assertIn("designer", reg)
        order = agents.CANON_ORDER
        self.assertLess(order.index("designer"), order.index("frontend"))
        self.assertTrue(reg["designer"].owns("app/globals.css"))
        self.assertFalse(reg["designer"].owns("app/api/users.ts"))   # forbidden

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

    def test_database_category_and_rich_files(self):
        db = [m for m in nx_packs.catalog() if m.get("category") == "database"]
        names = {m["name"] for m in db}
        self.assertTrue({"postgres", "mongodb"} <= names)            # reference packs
        self.assertGreaterEqual(len(db), 8)                          # a whole category
        for ref in ("postgres", "mongodb"):
            self.assertEqual(nx_packs.manifest(ref)["status"], "stable")
            d = nx_packs.pack_dir(ref)
            for f in ("anti-patterns.md", "performance.md", "security.md",
                      "prompts/specialist.md", "templates/migration.md"):
                self.assertTrue((d / f).is_file(), f"{ref} missing {f}")


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
