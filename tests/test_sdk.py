"""PR-9 — SDK registration, lookup, plugins, tools and event wiring."""
import unittest

import nx_sdk as sdk
from nx_core.kernel.engine import ExecutionMode
from nx_core.observability.events import EventBus
from nx_workflow.workflow import Step, Workflow, default_registry


class TestSDK(unittest.TestCase):
    def setUp(self):
        sdk.reset()

    def tearDown(self):
        sdk.reset()

    def test_register_and_get_adapter(self):
        class A:
            name = "x"
            def run(self, **k): ...
        sdk.register_adapter("x", A())
        self.assertIsNotNone(sdk.get_adapter("x"))

    def test_register_tool(self):
        sdk.register_tool("sast", lambda p: ["finding"])
        self.assertEqual(sdk.get_tool("sast")("p"), ["finding"])

    def test_register_workflow_visible_in_default_registry(self):
        wf = Workflow("audit-only", (Step("audit", engine="audit", mode=ExecutionMode.DRY_RUN),))
        sdk.register_workflow(wf)
        self.assertIn("audit-only", default_registry().names())
        self.assertIs(sdk.get_workflow("audit-only"), wf)

    def test_plugin_setup_runs(self):
        ran = {}
        class Plugin:
            name = "p"
            def setup(self, sdk_mod):
                ran["yes"] = True
                sdk_mod.register_tool("t", object())
        sdk.register_plugin("p", Plugin())
        self.assertTrue(ran.get("yes"))
        self.assertIsNotNone(sdk.get_tool("t"))

    def test_event_handlers_applied_to_bus(self):
        seen = []
        sdk.on("custom.event", lambda e: seen.append(e.type))
        bus = EventBus()
        self.assertEqual(sdk.apply_event_handlers(bus), 1)
        bus.emit("custom.event", {})
        self.assertEqual(seen, ["custom.event"])

    def test_registries_listed(self):
        sdk.register_agent("a", {"title": "A"})
        self.assertIn("a", sdk.registry("agents"))


if __name__ == "__main__":
    unittest.main()
