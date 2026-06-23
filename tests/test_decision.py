"""Prompt-3 — Decision Engine + Strategy/Reasoning/Risk/Estimation engines."""
import unittest

from nx_runtime.intelligence.decision import Decision, DecisionEngine, _layers
from nx_runtime.intelligence.estimation import EstimationEngine
from nx_runtime.intelligence.reasoning import ReasoningEngine
from nx_runtime.intelligence.risk import RiskEngine
from nx_runtime.intelligence.strategy import StrategyEngine
from nx_core.observability.events import EventBus
from nx_runtime.schedulers.dispatcher import AgentSelection


class TestRiskEngine(unittest.TestCase):
    def test_assess_returns_level_and_messages(self):
        r = RiskEngine().assess("Implement OAuth with tokens")
        self.assertEqual(r["level"], "high")
        self.assertGreater(r["score"], 0)
        self.assertTrue(r["messages"])


class TestEstimationEngine(unittest.TestCase):
    def test_cost_and_time(self):
        e = EstimationEngine().assess(agents=["backend", "database", "qa"], risk_score=2)
        self.assertGreater(e["estimated_cost_tokens"], 0)
        self.assertGreater(e["estimated_time_min_sequential"], 0)
        self.assertIn("confidence", e)

    def test_parallelism_reduces_time(self):
        seq = EstimationEngine().assess(agents=["a", "b", "c", "d"], parallelism=1)
        par = EstimationEngine().assess(agents=["a", "b", "c", "d"], parallelism=4)
        self.assertLess(par["estimated_time_min_parallel"],
                        seq["estimated_time_min_parallel"])


class TestStrategyEngine(unittest.TestCase):
    def test_code_request_gets_full_dev(self):
        se = StrategyEngine()
        sels = se.select_agents("Implement OAuth login")
        self.assertEqual(se.select_workflow("Implement OAuth login", sels), "full-dev")

    def test_docs_request_gets_plan_only(self):
        se = StrategyEngine()
        sels = se.select_agents("Update the README documentation")
        self.assertEqual(se.select_workflow("Update the README documentation", sels),
                         "plan-only")


class TestReasoningEngine(unittest.TestCase):
    def test_code_needs_review_and_qa(self):
        out = ReasoningEngine().reason(
            request="x", agents=["backend", "qa"], risk_level="low",
            risk_messages=[], parallelism=1,
            estimate={"effort_points": 3, "estimated_time_min_parallel": 6,
                      "estimated_cost_tokens": 6000, "confidence": 0.7})
        self.assertTrue(out["needs_review"])
        self.assertTrue(out["needs_qa"])
        self.assertFalse(out["parallelizable"])

    def test_docs_only_is_light(self):
        out = ReasoningEngine().reason(
            request="x", agents=["docs"], risk_level="minimal", risk_messages=[],
            parallelism=1, estimate={"effort_points": 1, "estimated_time_min_parallel": 2,
                                     "estimated_cost_tokens": 2000, "confidence": 0.9})
        self.assertFalse(out["needs_qa"])


class TestLayers(unittest.TestCase):
    def test_layers_group_independent_agents(self):
        sels = [
            AgentSelection("architect", True, "", 0, []),
            AgentSelection("database", True, "", 1, []),
            AgentSelection("backend", True, "", 2, ["database", "architect"]),
        ]
        layers = _layers(sels)
        self.assertIn("architect", layers[0])
        self.assertIn("database", layers[0])
        self.assertEqual(layers[1], ["backend"])


class TestDecisionEngine(unittest.TestCase):
    def test_full_decision_for_oauth(self):
        d = DecisionEngine().decide("Implement OAuth login with tokens and migration",
                                    arch={"has_tests": True, "is_monorepo": True})
        self.assertIsInstance(d, Decision)
        self.assertEqual(d.workflow, "full-dev")
        self.assertIn("security", d.agents)
        self.assertNotIn("frontend", d.agents)
        self.assertEqual(d.risk_level, "high")
        self.assertTrue(d.needs_review)
        self.assertTrue(d.needs_qa)
        self.assertTrue(d.parallelizable)            # architect/database/security
        self.assertGreaterEqual(d.parallelism, 2)
        self.assertGreater(d.estimated_cost_tokens, 0)
        self.assertGreater(d.estimated_time_min, 0)
        self.assertTrue(d.execution_order)
        self.assertTrue(d.rationale)

    def test_order_respects_dependencies(self):
        d = DecisionEngine().decide("Implement OAuth login with tokens")
        order = d.execution_order
        if "database" in order and "backend" in order:
            self.assertLess(order.index("database"), order.index("backend"))

    def test_emits_decision_made(self):
        bus = EventBus()
        DecisionEngine(bus=bus).decide("Add a backend endpoint")
        self.assertEqual(len(bus.history("decision.made")), 1)

    def test_records_adr_on_request(self):
        bus = EventBus()
        DecisionEngine(bus=bus).decide("Add a backend endpoint", record_adr=True)
        self.assertEqual(len(bus.history("decision.recorded")), 1)

    def test_summary_is_json_friendly(self):
        import json
        d = DecisionEngine().decide("Add a util")
        json.dumps(d.summary())  # must not raise (no AgentSelection objects)


if __name__ == "__main__":
    unittest.main()
