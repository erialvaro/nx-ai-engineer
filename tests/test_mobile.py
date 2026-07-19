"""Mobile module — the `mobile` Engineering Pack + the `mobile` agent + wiring.

React Native + Expo specialist: the pack ships the domain knowledge; the agent
owns RN/Expo files and runs after `frontend`; the `design-references` pack also
feeds it (tokens are platform-agnostic).
"""
import os
import tempfile
import unittest
from pathlib import Path

import nx_packs
from nx_core import agents
from nx_cli import orchestrator
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


class TestMobilePack(unittest.TestCase):
    def test_pack_catalogued_and_well_formed(self):
        self.assertIn("mobile", nx_packs.names())
        m = nx_packs.manifest("mobile")
        self.assertEqual(m["category"], "mobile")
        self.assertEqual(m["status"], "stable")
        self.assertEqual(m["applies_to"], ["mobile"])
        d = nx_packs.pack_dir("mobile")
        for f in nx_packs.REQUIRED:
            self.assertTrue((d / f).is_file(), f"missing {f}")
        for f in ("architecture.md", "navigation.md", "state-data.md",
                  "native-modules.md", "performance.md", "build-release.md",
                  "accessibility.md", "anti-patterns.md", "tooling.md",
                  "prompts/specialist.md", "templates/screen-spec.md"):
            self.assertTrue((d / f).is_file(), f"mobile pack missing {f}")

    def test_pack_declares_expo_and_eas_knowledge(self):
        d = nx_packs.pack_dir("mobile")
        build = (d / "build-release.md").read_text(encoding="utf-8").lower()
        self.assertIn("eas", build)
        ctx = (d / "context.md").read_text(encoding="utf-8").lower()
        self.assertIn("expo", ctx)
        # the mockup-app skill is referenced as prototyping tooling
        self.assertIn("mockup-app-skill", (d / "tooling.md").read_text(encoding="utf-8"))

    def test_pack_contains_no_python(self):
        self.assertEqual(list(nx_packs.pack_dir("mobile").rglob("*.py")), [])


class TestMobileAgent(unittest.TestCase):
    def setUp(self):
        self.reg = agents.registry()

    def test_registered_and_ordered_after_frontend(self):
        self.assertIn("mobile", self.reg)
        self.assertIn("mobile", agents.CANON_ORDER)
        order = agents.CANON_ORDER
        self.assertLess(order.index("frontend"), order.index("mobile"))

    def test_owns_mobile_files_not_web_or_server(self):
        m = self.reg["mobile"]
        for p in ("App.tsx", "app.json", "eas.json", "metro.config.js",
                  "src/screens/Home.tsx", "src/navigation/Root.tsx",
                  "components/Button.native.tsx"):
            self.assertTrue(m.owns(p), f"mobile should own {p}")
        for p in ("app/api/users.ts", "server/index.ts", "db/schema.sql"):
            self.assertFalse(m.owns(p), f"mobile must NOT own {p}")

    def test_routing_prefers_mobile_for_native_config(self):
        self.assertEqual(agents.route_file("eas.json", self.reg), "mobile")
        self.assertEqual(agents.route_file("src/screens/Profile.tsx", self.reg), "mobile")

    def test_keywords_cover_react_native_and_expo(self):
        kw = set(self.reg["mobile"].keywords)
        for k in ("react native", "expo", "eas", "mobile", "ios", "android"):
            self.assertIn(k, kw)

    def test_agent_template_present(self):
        tpl = (Path(orchestrator.__file__).resolve().parent
               / "_template" / "agents" / "mobile.md")
        self.assertTrue(tpl.is_file())


class TestMobileContract(unittest.TestCase):
    def test_mobile_pack_attaches_to_mobile_agent(self):
        with _Home(["mobile"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            c = cb.build("Build a booking app", "mobile")
            self.assertIn("mobile", c.packs())
            self.assertTrue(c.requirements["validations"])

    def test_mobile_agent_receives_design_reference(self):
        with _Home(["mobile", "design-references"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            c = cb.build("App de agendamento para um salão de beleza de luxo", "mobile")
            self.assertIsNotNone(c.design_reference)
            self.assertEqual(c.design_reference["id"], "odara-li")


if __name__ == "__main__":
    unittest.main()
