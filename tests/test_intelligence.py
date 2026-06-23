"""Intelligence layer — Risk and Estimation tests."""
import unittest
from dataclasses import dataclass, field

from nx_runtime.intelligence import estimation, risk


@dataclass
class _Sub:
    agent: str
    areas: list = field(default_factory=list)


@dataclass
class _Plan:
    description: str
    involved_agents: list = field(default_factory=list)
    subtasks: list = field(default_factory=list)


class TestRisk(unittest.TestCase):
    def test_high_for_auth(self):
        risks = risk.analyze("Implement OAuth login with tokens")
        self.assertEqual(risk.level(risks), "high")
        self.assertGreater(risk.score(risks), 0)

    def test_domain_rules_become_risks(self):
        risks = risk.analyze("add field", config={"domain_rules": ["No cross-tenant access"]})
        self.assertTrue(any("cross-tenant" in r.message for r in risks))

    def test_no_tests_flagged(self):
        risks = risk.analyze("simple change", arch={"has_tests": False})
        self.assertTrue(any("lacks tests" in r.message for r in risks))

    def test_minimal_when_nothing(self):
        self.assertEqual(risk.level([]), "minimal")


class TestEstimation(unittest.TestCase):
    def test_scales_with_scope(self):
        small = _Plan("tweak css", ["frontend"], [_Sub("frontend", ["web"])])
        big = _Plan("Implement OAuth with tokens and migration",
                    ["architect", "security", "backend", "database", "qa", "reviewer"],
                    [_Sub("backend", ["api", "services"]), _Sub("database", ["db"])])
        e_small = estimation.estimate(small)
        e_big = estimation.estimate(big)
        self.assertLess(e_small.effort_points, e_big.effort_points)
        self.assertGreaterEqual(e_big.blast_radius, e_small.blast_radius)
        self.assertLessEqual(e_big.confidence, e_small.confidence)

    def test_confidence_bounds(self):
        e = estimation.estimate(_Plan("x", ["backend"], [_Sub("backend")]))
        self.assertGreaterEqual(e.confidence, 0.2)
        self.assertLessEqual(e.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
