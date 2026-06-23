"""PR-4 — Context Engine tests (resolvers, ranking, cache, reduction)."""
import os
import tempfile
import unittest
from pathlib import Path

from nx_core.foundation import util
from nx_core.kernel.domain import Subtask
from nx_knowledge.memory import cache as cache_mod
from nx_knowledge.memory import context as ctx_mod
from nx_knowledge.memory.context import ContextBuilder, FilesResolver
from nx_core.observability.events import EventBus


class _Sandbox:
    """Create a throwaway project and point AIES_HOME at its .ai-project."""
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "apps" / "api" / "services").mkdir(parents=True)
        (root / "apps" / "web" / "components").mkdir(parents=True)
        (root / "tests").mkdir()
        (root / "docs").mkdir()
        (root / "apps/api/services/auth_service.py").write_text("x=1", encoding="utf-8")
        (root / "apps/api/routes.py").write_text("x=1", encoding="utf-8")
        (root / "apps/web/components/Btn.tsx").write_text("x=1", encoding="utf-8")
        (root / "tests/test_auth.py").write_text("x=1", encoding="utf-8")
        (root / "docs/auth.md").write_text("x", encoding="utf-8")
        (root / "pyproject.toml").write_text("[project]", encoding="utf-8")
        (root / ".ai-project").mkdir()
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(root / ".ai-project")
        return root

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        self.tmp.cleanup()


def _sub(agent="backend", objective="implement auth service", areas=None):
    return Subtask(id=agent, agent=agent, objective=objective,
                   areas=areas or ["apps/api"], acceptance=["tests pass"])


class TestContextBuilder(unittest.TestCase):
    def test_backend_gets_relevant_not_everything(self):
        with _Sandbox():
            res = ContextBuilder().build(agent="backend", subtask=_sub(), use_cache=False)
            ctx = res.context
            # backend-owned/service files included; the React component is not.
            joined = " ".join(ctx.files + ctx.services)
            self.assertIn("apps/api/services/auth_service.py", joined)
            self.assertNotIn("Btn.tsx", " ".join(ctx.files))
            self.assertGreater(res.estimated_reduction, 0)
            self.assertLess(res.included_files, res.total_files)

    def test_services_and_apis_resolved(self):
        with _Sandbox():
            res = ContextBuilder().build(agent="backend", subtask=_sub(), use_cache=False)
            self.assertTrue(any("auth_service" in s for s in res.context.services))
            self.assertTrue(any("routes" in a for a in res.context.apis))

    def test_docs_and_tests_resolved(self):
        with _Sandbox():
            res = ContextBuilder().build(agent="backend", subtask=_sub(), use_cache=False)
            self.assertTrue(any(d.endswith(".md") for d in res.context.docs))
            self.assertTrue(any("test" in t for t in res.context.tests))

    def test_reduction_metric_in_range(self):
        with _Sandbox():
            res = ContextBuilder().build(agent="backend", subtask=_sub(), use_cache=False)
            self.assertGreaterEqual(res.estimated_reduction, 0.0)
            self.assertLessEqual(res.estimated_reduction, 1.0)

    def test_cache_hit_on_second_build(self):
        with _Sandbox():
            b = ContextBuilder()
            first = b.build(agent="backend", subtask=_sub())
            self.assertFalse(first.cached)
            second = b.build(agent="backend", subtask=_sub())
            self.assertTrue(second.cached)
            self.assertEqual(first.context.files, second.context.files)

    def test_cache_clear(self):
        with _Sandbox():
            ContextBuilder().build(agent="backend", subtask=_sub())
            self.assertGreaterEqual(cache_mod.clear(), 1)

    def test_emits_context_built(self):
        with _Sandbox():
            bus = EventBus()
            ContextBuilder(bus=bus).build(agent="backend", subtask=_sub(), use_cache=False)
            evs = bus.history("context.built")
            self.assertEqual(len(evs), 1)
            self.assertIn("estimated_reduction", evs[0].payload)


class TestResolverProtocol(unittest.TestCase):
    def test_files_resolver_is_resolver(self):
        self.assertIsInstance(FilesResolver(), ctx_mod.Resolver)


if __name__ == "__main__":
    unittest.main()
