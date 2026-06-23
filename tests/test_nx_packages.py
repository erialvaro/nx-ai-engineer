"""The 8 nx_* packages import independently, deep submodules resolve, and the
split knowledge layer is re-aggregated without duplicating objects.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _d in (ROOT / "packages").glob("nx-*"):
    p = str(_d)
    if p not in sys.path:
        sys.path.insert(0, p)


class TestNxPackagesImport(unittest.TestCase):
    def test_all_eight_packages_import(self):
        import nx_cli  # noqa: F401
        import nx_core  # noqa: F401
        import nx_knowledge  # noqa: F401
        import nx_obsidian  # noqa: F401
        import nx_providers  # noqa: F401
        import nx_runtime  # noqa: F401
        import nx_sdk  # noqa: F401
        import nx_workflow  # noqa: F401
        self.assertRegex(nx_core.__version__, r"^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?$")

    def test_deep_submodules_resolve(self):
        from nx_core.kernel.domain import Node  # noqa: F401
        from nx_core.kernel.engine import BaseEngine  # noqa: F401
        from nx_knowledge.knowledge.engine import KnowledgeEngine  # noqa: F401
        from nx_knowledge.memory.context import ContextBuilder  # noqa: F401
        from nx_providers.knowledge.filesystem import FilesystemProvider  # noqa: F401
        from nx_obsidian.knowledge.obsidian_sync import ObsidianSync  # noqa: F401
        from nx_runtime.schedulers.cluster import ExecutionCluster  # noqa: F401
        from nx_runtime.kernel.pipeline import Pipeline  # noqa: F401
        from nx_sdk import register_agent  # noqa: F401
        from nx_workflow.workflow import Workflow  # noqa: F401

    def test_knowledge_aggregate_is_not_a_copy(self):
        # The knowledge aggregate re-exports the SAME provider objects across the
        # split packages — no duplicated implementation.
        from nx_knowledge.knowledge import ADRProvider
        from nx_providers.knowledge.adr import ADRProvider as Direct
        self.assertIs(ADRProvider, Direct)


if __name__ == "__main__":
    unittest.main()
