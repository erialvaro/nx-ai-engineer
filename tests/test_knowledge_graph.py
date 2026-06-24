"""Knowledge Graph — automatic relationships used to enrich agent context."""
import os
import tempfile
import unittest
from pathlib import Path

from nx_knowledge.evolution.project_evolution import ProjectEvolutionEngine
from nx_knowledge.knowledge.engine import KnowledgeEngine
from nx_providers.knowledge.graph import KnowledgeGraph, KnowledgeGraphBuilder
from nx_knowledge.memory.brain import ProjectBrain


class _Home:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        cfg = Path(self.tmp.name) / ".ai-project-assistant"
        cfg.mkdir()
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(cfg)
        return cfg

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        self.tmp.cleanup()


def _seed(brain):
    brain.put("architecture", "current", {"frameworks": ["FastAPI"]})
    ProjectEvolutionEngine(brain).evolve({
        "request": "Fix OAuth token bug",
        "files_changed": [
            "apps/api/services/auth_service.py", "apps/api/routes.py",
            "libs/db/migrations/0002_tokens.sql", "libs/db/models/token.py",
            "tests/test_auth.py"],
        "strategy_success": True, "failures": 0, "retries": 0, "workflow": "full-dev",
        "agents_used": ["backend", "database", "qa"],
        "decisions": [{"workflow": "full-dev"}]})


class TestGraphBuild(unittest.TestCase):
    def test_chain_edges_inferred(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            g = KnowledgeGraphBuilder(b).build()
            kinds = {e.kind for e in g.edges}
            # the canonical chain + relations
            self.assertTrue({"serves", "uses", "migrates", "covers", "delivers"} <= kinds)

    def test_typed_nodes(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            g = KnowledgeGraphBuilder(b).build()
            types = {n.type for n in g.nodes.values()}
            self.assertTrue({"service", "api", "entity", "migration", "test",
                             "feature", "bug"} <= types)

    def test_migration_typed_separately(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            g = KnowledgeGraphBuilder(b).build()
            migs = g.nodes_of_type("migration")
            self.assertTrue(any("migration" in m.meta.get("path", "") for m in migs))

    def test_stats_and_mermaid(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            g = KnowledgeGraphBuilder(b).build()
            self.assertGreater(g.stats()["nodes"], 0)
            self.assertIn("```mermaid", g.to_mermaid())


class TestRelatedElements(unittest.TestCase):
    def test_related_to_path(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            g = KnowledgeGraphBuilder(b).build()
            rel = g.related_elements(["apps/api/services/auth_service.py"])
            # the service is connected to its API, test and entity
            self.assertIn("apps/api/routes.py", rel.get("api", []))
            self.assertIn("tests/test_auth.py", rel.get("test", []))

    def test_unknown_path_empty(self):
        with _Home():
            g = KnowledgeGraphBuilder(ProjectBrain()).build()
            self.assertEqual(g.related_elements(["nope.py"]), {})


class TestEngineAndContextEnrichment(unittest.TestCase):
    def test_engine_graph_and_enrich(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            eng = KnowledgeEngine(b)
            self.assertIsInstance(eng.graph(), KnowledgeGraph)
            rel = eng.enrich_context(["apps/api/services/auth_service.py"])
            self.assertTrue(rel)

    def test_context_is_enriched_by_graph(self):
        with _Home() as cfg:
            root = cfg.parent
            # real files so the Context Engine's file list seeds graph enrichment
            (root / "apps/api/services").mkdir(parents=True)
            (root / "apps/api/services/auth_service.py").write_text("x=1", encoding="utf-8")
            b = ProjectBrain(); _seed(b)
            eng = KnowledgeEngine(b)
            from nx_core.kernel.domain import Subtask
            from nx_knowledge.memory.context import ContextBuilder
            # craft a subtask whose context files include the service
            res = ContextBuilder(knowledge=eng).build(
                agent="backend",
                subtask=Subtask(id="backend", agent="backend",
                                objective="auth service", areas=["apps/api"]),
                use_cache=False)
            # graph enrichment adds related APIs/tests even if resolvers missed them
            enriched = set(res.context.apis) | set(res.context.tests)
            self.assertTrue(any("routes" in x or "test_auth" in x for x in enriched))

    def test_enrichment_never_replaces_reasoning(self):
        # The engine exposes only data (paths/labels) — no decisions/answers.
        with _Home():
            b = ProjectBrain(); _seed(b)
            rel = KnowledgeEngine(b).enrich_context(["apps/api/services/auth_service.py"])
            for items in rel.values():
                self.assertTrue(all(isinstance(x, str) for x in items))


if __name__ == "__main__":
    unittest.main()
