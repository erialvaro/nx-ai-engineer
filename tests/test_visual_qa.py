"""Visual-QA module — the `visual-qa` Engineering Pack + the `responsive` and
`visual-qa` agents + scaffold wiring.

The pack ships the browser-driven QA doctrine (device matrix, overflow/contrast/
CLS gates, Lighthouse >= 95, BackstopJS baselines); the `responsive` agent is the
mobile-first web developer; the `visual-qa` agent runs the loop and gates the
merge. Both are fed by the pack; `responsive` also receives a design reference.
"""
import os
import tempfile
import unittest
from pathlib import Path

import nx_packs
from nx_core import agents
from nx_cli import bootstrap, orchestrator
from nx_knowledge.knowledge.contract import ContractBuilder
from nx_knowledge.knowledge.registry import default_registry


class _Home:
    def __init__(self, packs):
        self.packs = packs

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / ".ai-project-assistant"
        (root / "packs").mkdir(parents=True)
        for p in self.packs:
            nx_packs.install(p, root / "packs")
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(root)
        return root

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        self.tmp.cleanup()


class TestVisualQaPack(unittest.TestCase):
    def test_pack_catalogued_and_well_formed(self):
        self.assertIn("visual-qa", nx_packs.names())
        m = nx_packs.manifest("visual-qa")
        self.assertEqual(m["category"], "qa")
        self.assertEqual(m["status"], "stable")
        for agent in ("visual-qa", "responsive", "frontend", "mobile", "qa"):
            self.assertIn(agent, m["applies_to"], f"pack should feed {agent}")
        d = nx_packs.pack_dir("visual-qa")
        for f in nx_packs.REQUIRED:
            self.assertTrue((d / f).is_file(), f"missing {f}")
        for f in ("device-matrix.md", "workflow.md", "responsive.md",
                  "accessibility.md", "performance.md", "anti-patterns.md",
                  "tooling.md", "prompts/specialist.md",
                  "templates/visual-qa-report.md"):
            self.assertTrue((d / f).is_file(), f"visual-qa pack missing {f}")

    def test_tooling_documents_the_stack(self):
        tooling = (nx_packs.pack_dir("visual-qa") / "tooling.md").read_text(encoding="utf-8")
        for tool in ("Playwright", "Playwright MCP", "BrowserTools MCP",
                     "Lighthouse CI", "BackstopJS", "Storybook", "React DevTools",
                     "Tailwind CSS IntelliSense", "ESLint", "Prettier",
                     "Android Studio", "Genymotion", "Chrome DevTools"):
            self.assertIn(tool, tooling, f"tooling.md must document {tool}")

    def test_policies_state_the_gates(self):
        pol = (nx_packs.pack_dir("visual-qa") / "policies.md").read_text(encoding="utf-8").lower()
        for gate in ("overflow", "contrast", "cls", "lighthouse", "44"):
            self.assertIn(gate, pol, f"policies.md should gate {gate}")

    def test_device_matrix_lists_the_viewports(self):
        dm = (nx_packs.pack_dir("visual-qa") / "device-matrix.md").read_text(encoding="utf-8")
        for w in ("360", "390", "768", "1024", "1366", "1920"):
            self.assertIn(w, dm, f"device-matrix.md missing width {w}")

    def test_pack_contains_no_python(self):
        self.assertEqual(list(nx_packs.pack_dir("visual-qa").rglob("*.py")), [])


class TestVisualQaAgents(unittest.TestCase):
    def setUp(self):
        self.reg = agents.registry()

    def test_both_agents_registered_and_ordered(self):
        for name in ("responsive", "visual-qa"):
            self.assertIn(name, self.reg)
            self.assertIn(name, agents.CANON_ORDER)
        order = agents.CANON_ORDER
        # responsive develops right after frontend, before mobile
        self.assertLess(order.index("frontend"), order.index("responsive"))
        self.assertLess(order.index("responsive"), order.index("mobile"))
        # visual-qa gates after qa, before reviewer
        self.assertLess(order.index("qa"), order.index("visual-qa"))
        self.assertLess(order.index("visual-qa"), order.index("reviewer"))

    def test_responsive_owns_responsive_files_not_server(self):
        r = self.reg["responsive"]
        for p in ("src/Card.responsive.tsx", "components/responsive/Grid.tsx",
                  "src/layouts/Shell.tsx", "ui/Button.stories.tsx"):
            self.assertTrue(r.owns(p), f"responsive should own {p}")
        for p in ("app/api/users.ts", "server/index.ts", "db/schema.sql"):
            self.assertFalse(r.owns(p), f"responsive must NOT own {p}")

    def test_visual_qa_owns_visual_infra_not_product(self):
        v = self.reg["visual-qa"]
        for p in ("playwright.config.ts", "backstop.json", "lighthouserc.json",
                  "tests/visual/home.visual.spec.ts", "e2e/visual/flow.spec.ts"):
            self.assertTrue(v.owns(p), f"visual-qa should own {p}")
        for p in ("src/components/Button.tsx", "app/api/users.ts"):
            self.assertFalse(v.owns(p), f"visual-qa must NOT own product source {p}")

    def test_routing_prefers_visual_qa_for_visual_specs(self):
        # more specific than the generic `qa` globs -> visual-qa wins
        self.assertEqual(agents.route_file("tests/visual/home.visual.spec.ts", self.reg), "visual-qa")
        self.assertEqual(agents.route_file("playwright.config.ts", self.reg), "visual-qa")

    def test_keywords_cover_the_domain(self):
        rk = set(self.reg["responsive"].keywords)
        for k in ("responsive", "mobile-first", "breakpoint", "overflow"):
            self.assertIn(k, rk)
        vk = set(self.reg["visual-qa"].keywords)
        for k in ("playwright", "lighthouse", "visual regression", "device matrix"):
            self.assertIn(k, vk)

    def test_agent_templates_present(self):
        base = Path(orchestrator.__file__).resolve().parent / "_template" / "agents"
        self.assertTrue((base / "responsive.md").is_file())
        self.assertTrue((base / "visual-qa.md").is_file())


class TestVisualQaContract(unittest.TestCase):
    def test_pack_attaches_to_visual_qa_and_responsive(self):
        with _Home(["visual-qa"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            for agent in ("visual-qa", "responsive", "frontend"):
                c = cb.build("Fix responsive layout and gate Lighthouse", agent)
                self.assertIn("visual-qa", c.packs(), f"{agent} should get the visual-qa pack")

    def test_responsive_receives_design_reference(self):
        with _Home(["visual-qa", "design-references"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            c = cb.build("Landing responsiva para um salão de beleza de luxo", "responsive")
            self.assertIsNotNone(c.design_reference)
            self.assertEqual(c.design_reference["id"], "odara-li")


class TestVisualQaScaffold(unittest.TestCase):
    def test_scaffold_ships_the_visual_qa_loop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, *_ = bootstrap.new_project("qa-demo", tmp, stack="cloud-agnostic")
            for rel in ("frontend/playwright.config.ts",
                        "frontend/tests/visual/responsive.spec.ts",
                        "frontend/backstop.json",
                        "frontend/lighthouserc.json",
                        "frontend/.storybook/main.ts",
                        "frontend/.storybook/preview.ts",
                        ".github/workflows/visual-qa.yml"):
                self.assertTrue((root / rel).is_file(), f"scaffold missing {rel}")
            # dotdir sources must not leak their `dot.` name
            self.assertFalse((root / "frontend/dot.storybook").exists())
            # npm scripts wired
            pkg = (root / "frontend/package.json").read_text(encoding="utf-8")
            for script in ("test:visual", "lhci", "test:regression", "storybook"):
                self.assertIn(script, pkg, f"package.json missing script {script}")


if __name__ == "__main__":
    unittest.main()
