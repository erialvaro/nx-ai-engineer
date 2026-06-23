"""PR-6 — Governance gates and Delivery Engine tests."""
import unittest

from nx_core.governance import checklists, policies
from nx_core.governance import quality_gates as gates


class TestGates(unittest.TestCase):
    def test_protected_paths_blocks(self):
        r = gates.protected_paths_gate(["src/billing/charge.py"], ["**/billing/**"])
        self.assertFalse(r.passed)

    def test_protected_paths_ok(self):
        r = gates.protected_paths_gate(["src/util.py"], ["**/billing/**"])
        self.assertTrue(r.passed)

    def test_tests_on_critical(self):
        review = {"critical_changes": ["auth.py"], "without_tests": ["auth.py"]}
        self.assertFalse(gates.tests_present_gate(review).passed)
        review2 = {"critical_changes": ["auth.py"], "without_tests": ["other.py"]}
        self.assertTrue(gates.tests_present_gate(review2).passed)

    def test_no_failed_nodes(self):
        self.assertFalse(gates.no_failed_nodes_gate({"nodes": [{"id": "x", "state": "FAILED"}]}).passed)
        self.assertTrue(gates.no_failed_nodes_gate({"nodes": [{"id": "x", "state": "COMPLETED"}]}).passed)

    def test_evaluate_aggregates(self):
        report = gates.evaluate([
            gates.protected_paths_gate(["a"], []),
            gates.tests_present_gate({}),
        ])
        self.assertTrue(report["passed"])
        self.assertEqual(report["blocking"], [])


class TestPoliciesChecklists(unittest.TestCase):
    def test_domain_rules_merged(self):
        pol = policies.all_policies({"domain_rules": ["No cross-tenant access"]})
        self.assertTrue(any("cross-tenant" in p for p in pol))

    def test_checklist_for_agent(self):
        cl = checklists.for_agent("database")
        self.assertIn("Migration reversible", cl)
        self.assertTrue(any("Tests" in c for c in cl))


class TestDeliveryBuild(unittest.TestCase):
    def test_pr_contains_sections(self):
        from nx_runtime.engines.delivery import build_pr
        task = {"id": "t1", "description": "Add feature"}
        review = {"files": ["a.py"], "total_changed": 1, "critical_changes": [],
                  "without_tests": []}
        report = gates.evaluate([gates.protected_paths_gate(["a.py"], [])])
        md = build_pr(task, review, report)
        for section in ("## Summary", "## Impact", "## Quality gates", "## Rollback"):
            self.assertIn(section, md)


if __name__ == "__main__":
    unittest.main()
