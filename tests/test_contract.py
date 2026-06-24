"""Engineering Contract — auto-application (applies_to + override), requirements,
rendering, and delivery enforcement.
"""
import os
import tempfile
import unittest
from pathlib import Path

import nx_packs
from nx_knowledge.knowledge.contract import ContractBuilder, EngineeringContract
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


class TestAutoApplication(unittest.TestCase):
    def test_applies_to_attaches_by_agent_and_star(self):
        with _Home(["security", "lgpd", "multi-tenant", "cloud"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            backend = set(cb.build("Add login", "backend").packs())
            self.assertIn("security", backend)       # "*"
            self.assertIn("lgpd", backend)            # "*"
            self.assertIn("multi-tenant", backend)    # backend in applies_to
            self.assertNotIn("cloud", backend)        # devops-only
            devops = set(cb.build("Provision", "devops").packs())
            self.assertIn("cloud", devops)
            self.assertNotIn("multi-tenant", devops)

    def test_database_packs_attach_to_specialist_agents(self):
        with _Home(["postgres", "mongodb"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            rel = set(cb.build("Add orders table", "database-relational").packs())
            self.assertIn("postgres", rel)        # relational pack -> relational agent
            self.assertNotIn("mongodb", rel)      # nosql pack does not attach to relational
            nosql = set(cb.build("Model orders documents", "database-nosql").packs())
            self.assertIn("mongodb", nosql)
            self.assertNotIn("postgres", nosql)
            # the same pack also serves the Database Reviewer (shared knowledge)
            rev = set(cb.build("Review schema", "database-reviewer").packs())
            self.assertIn("postgres", rev)
            self.assertIn("mongodb", rev)

    def test_config_override_adds_and_excludes(self):
        with _Home(["billing", "ai"]):
            cfg = {"contracts": {"agents": {"backend": {"packs": ["ai"], "exclude": ["billing"]}}}}
            cb = ContractBuilder(config=cfg, registry=default_registry(config=cfg))
            packs = set(cb.build("x", "backend").packs())
            self.assertIn("ai", packs)         # added via override (ai is ai-only by default)
            self.assertNotIn("billing", packs)  # excluded (billing applies to backend by default)


class TestContractContent(unittest.TestCase):
    def test_requirements_constraints_and_render(self):
        with _Home(["security", "testing"]):
            cb = ContractBuilder(config={"domain_rules": ["Never break tenant isolation"]},
                                 registry=default_registry())
            c = cb.build("Implement login", "backend", files=["auth.py"], areas=["api/auth"])
            self.assertIsInstance(c, EngineeringContract)
            self.assertTrue(c.requirements["tests"])
            self.assertTrue(c.requirements["validations"])
            self.assertIn("Never break tenant isolation", c.constraints)
            self.assertIn("auth.py", c.context["files"])
            txt = c.to_text()
            for section in ("task:", "agent:", "context:", "engineering:", "constraints:",
                            "requirements:", "brain:"):
                self.assertIn(section, txt)
            self.assertIn("agent", c.as_dict())

    def test_requirements_for_aggregates(self):
        with _Home(["security", "testing"]):
            agg = ContractBuilder(config={}, registry=default_registry()).requirements_for(["backend"])
            self.assertTrue(agg["mandates_tests"])
            self.assertIn("security", agg["packs"])
            self.assertTrue(agg["validations"])

    def test_no_packs_means_empty_engineering(self):
        with _Home([]):
            c = ContractBuilder(config={}, registry=default_registry()).build("x", "backend")
            self.assertEqual(c.engineering, [])


class TestDeliveryEnforcement(unittest.TestCase):
    def test_contract_gate_blocks_untested_when_mandated(self):
        from nx_runtime.engines.delivery import _contract_gate
        req = {"packs": ["security"], "mandates_tests": True}
        self.assertFalse(_contract_gate(req, {"without_tests": ["a.py"]}).passed)   # blocks
        self.assertTrue(_contract_gate(req, {"without_tests": []}).passed)          # ok
        self.assertTrue(_contract_gate({"packs": []}, {"without_tests": ["a.py"]}).passed)  # no contract


if __name__ == "__main__":
    unittest.main()
