"""PR-3 — Agent Dispatcher + Strategy Pattern tests."""
import unittest

from nx_core.observability.events import EventBus
from nx_runtime.schedulers.dispatcher import (
    AgentDispatcher, AgentSelection, RuleBasedStrategy, SelectionStrategy,
)


def names(selections, *, selected):
    return {s.agent for s in selections if s.selected is selected}


class TestRuleBasedSelection(unittest.TestCase):
    def setUp(self):
        self.d = AgentDispatcher()

    def test_oauth_selects_expected_and_never_frontend(self):
        sels = self.d.dispatch(description="Implement OAuth login with tokens")
        chosen = names(sels, selected=True)
        self.assertTrue({"architect", "security", "backend", "database",
                         "qa", "reviewer", "delivery"} <= chosen)
        self.assertNotIn("frontend", chosen)
        self.assertIn("frontend", names(sels, selected=False))

    def test_ui_task_selects_frontend_not_db_or_security(self):
        sels = self.d.dispatch(description="Build a settings UI form with validation")
        chosen = names(sels, selected=True)
        self.assertIn("frontend", chosen)
        self.assertNotIn("database", chosen)
        self.assertNotIn("security", chosen)
        # quality gates always present
        self.assertTrue({"qa", "reviewer", "delivery"} <= chosen)

    def test_single_area_has_no_architect(self):
        sels = self.d.dispatch(description="Tweak the CSS of the header component")
        chosen = names(sels, selected=True)
        self.assertNotIn("architect", chosen)

    def test_selection_is_dependency_ordered(self):
        sels = AgentDispatcher.selected(
            self.d.dispatch(description="Implement OAuth login with tokens"))
        order = {s.agent: s.order for s in sels}
        for s in sels:
            for dep in s.depends_on:
                self.assertLess(order[dep], s.order,
                                f"{dep} must come before {s.agent}")

    def test_meta_agents_never_appear(self):
        sels = self.d.dispatch(description="anything")
        agents = {s.agent for s in sels}
        self.assertNotIn("planner", agents)
        self.assertNotIn("task-manager", agents)

    def test_reasons_present(self):
        sels = self.d.dispatch(description="Implement OAuth login with tokens")
        for s in sels:
            self.assertTrue(s.reason)

    def test_emits_event(self):
        bus = EventBus()
        AgentDispatcher(bus=bus).dispatch(description="Implement OAuth")
        self.assertEqual(len(bus.history("agent.selected")), 1)


class TestStrategySwap(unittest.TestCase):
    def test_custom_strategy_is_used(self):
        class Fixed:
            name = "fixed"
            def select(self, *, description, registry):
                return [AgentSelection("backend", True, "fixed pick", 0, [])]
        d = AgentDispatcher(strategy=Fixed())
        self.assertEqual(d.strategy_name, "fixed")
        sels = d.dispatch(description="whatever")
        self.assertEqual(names(sels, selected=True), {"backend"})

    def test_rulebased_satisfies_protocol(self):
        self.assertIsInstance(RuleBasedStrategy(), SelectionStrategy)


if __name__ == "__main__":
    unittest.main()
