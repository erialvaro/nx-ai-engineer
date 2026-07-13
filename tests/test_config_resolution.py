"""Regression: knowledge resolution can't hijack to (or hang on) the wrong root.

A stray `.ai-project-assistant` in a distant ancestor (e.g. the user's home) used
to hijack `config_root`, because it searched up from the *install* location. That
made the whole project scan/sync target — and hang on — an unrelated, huge tree
(the Obsidian vault detection walked it unbounded). These tests lock the fix.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from nx_core.foundation import util
from nx_obsidian.knowledge.obsidian import ObsidianProvider


class TestConfigRootResolution(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.pop("AIES_HOME", None)
        self._cwd = Path.cwd()

    def tearDown(self):
        os.chdir(self._cwd)
        if self._home is not None:
            os.environ["AIES_HOME"] = self._home

    def test_closest_home_wins_over_ancestor(self):
        # outer/.ai-project-assistant AND outer/inner/.ai-project-assistant:
        # running from inner must resolve to inner's, never the ancestor's.
        with tempfile.TemporaryDirectory() as tmp:
            outer = Path(tmp).resolve() / "outer"
            inner = outer / "inner"
            (outer / util.CONFIG_DIRNAME).mkdir(parents=True)
            (inner / util.CONFIG_DIRNAME).mkdir(parents=True)
            os.chdir(inner)
            try:
                self.assertEqual(util.config_root(), inner / util.CONFIG_DIRNAME)
                self.assertEqual(util.project_root(), inner)
            finally:
                os.chdir(self._cwd)  # leave tmp before it is cleaned up (Windows)

    def test_explicit_start_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp).resolve() / "proj"
            (proj / util.CONFIG_DIRNAME).mkdir(parents=True)
            self.assertEqual(util.config_root(proj), proj / util.CONFIG_DIRNAME)

    def test_aies_home_env_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve() / util.CONFIG_DIRNAME
            home.mkdir(parents=True)
            os.environ["AIES_HOME"] = str(home)
            self.assertEqual(util.config_root(), home)


class TestObsidianDetectBounded(unittest.TestCase):
    def test_detect_returns_none_without_vault(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a" / "b" / "c").mkdir(parents=True)
            self.assertIsNone(ObsidianProvider(root=root)._detect())


if __name__ == "__main__":
    unittest.main()
