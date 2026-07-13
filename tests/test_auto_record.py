"""Ambient recording (`auto_record`): from the moment `.ai-project-assistant`
exists at the project root, knowledge-producing commands persist to the Project
Brain and sync the vault automatically — no explicit `nxai knowledge sync` needed.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from nx_cli import bootstrap, orchestrator
from nx_core import config as config_mod


class TestAutoRecord(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("AIES_HOME")

    def tearDown(self):
        if self._home is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._home

    def test_default_is_on(self):
        self.assertIs(config_mod.DEFAULTS.get("auto_record"), True)

    def test_records_to_brain_and_syncs_without_asking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, *_ = bootstrap.init(tmp)          # `.ai-project-assistant` at root
            os.environ["AIES_HOME"] = str(root)
            cfg = config_mod.load(root)
            self.assertTrue(cfg["auto_record"])
            # a knowledge-producing command's ambient hook — no `knowledge sync` call
            orchestrator._auto_record(cfg, note="plan",
                                      record={"kind": "plan", "goal": "Add OAuth login"})
            found = any("Add OAuth login" in p.read_text(encoding="utf-8", errors="ignore")
                        for p in (root / "brain").rglob("*") if p.is_file())
            self.assertTrue(found, "the plan/goal was not recorded to the Brain")

    def test_off_switch_disables_recording(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, *_ = bootstrap.init(tmp)
            os.environ["AIES_HOME"] = str(root)
            orchestrator._auto_record({"auto_record": False},
                                      record={"kind": "plan", "goal": "SHOULD-NOT-PERSIST"})
            found = any("SHOULD-NOT-PERSIST" in p.read_text(encoding="utf-8", errors="ignore")
                        for p in (root / "brain").rglob("*") if p.is_file())
            self.assertFalse(found)


if __name__ == "__main__":
    unittest.main()
