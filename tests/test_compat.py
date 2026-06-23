"""Cross-package import compatibility — the monorepo split did not break public
imports and the logical homes resolve to the same engine objects (no duplication).
"""
import unittest


class TestCoreImports(unittest.TestCase):
    def test_core_engines_import(self):
        from nx_core import (  # noqa: F401
            agents, analyzer, config, locks, planner, review, tasks, util, worktree,
        )
        self.assertTrue(hasattr(planner, "build_plan"))
        self.assertTrue(hasattr(analyzer, "analyze"))
        self.assertTrue(hasattr(review, "build"))
        self.assertTrue(hasattr(locks, "acquire"))

    def test_version_present(self):
        import nx_core
        # SemVer, optionally with a pre-release tag (e.g. 5.0.0-rc1).
        self.assertRegex(nx_core.__version__, r"^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?$")


class TestLogicalHomes(unittest.TestCase):
    def test_foundation_reexports(self):
        from nx_core.foundation import config, util
        self.assertTrue(hasattr(util, "config_root"))
        self.assertTrue(hasattr(config, "load"))

    def test_intelligence_planner_is_same_engine(self):
        from nx_core import planner as core
        from nx_runtime.intelligence import planner as intel
        self.assertIs(intel.build_plan, core.build_plan)
        self.assertIs(intel.execution_order, core.execution_order)

    def test_engines_home_resolves(self):
        from nx_core import analyzer as core
        from nx_runtime.engines import analyzer as homed
        from nx_runtime.engines import audit
        self.assertIs(homed.analyze, core.analyze)
        self.assertIs(audit, core)  # audit lives in the analyzer module today

    def test_sdk_registries_exist(self):
        import nx_sdk as sdk
        for kind in ("agents", "engines", "workflows", "adapters", "plugins", "tools"):
            self.assertIsInstance(sdk.registry(kind), dict)


if __name__ == "__main__":
    unittest.main()
