"""ADRs placed in the `decisions` Brain facet are indexed, and free-form Brain
markdown docs (briefs / requirements / context) are surfaced (retrievable) —
even though the generic providers skip the `.ai-project-assistant` home.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from nx_cli import bootstrap
from nx_knowledge.memory.brain import ProjectBrain
from nx_providers.knowledge.adr import ADRProvider
from nx_providers.knowledge.project_brain import ProjectBrainProvider


class TestAdrDecisionsAndBrainDocs(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("AIES_HOME")

    def tearDown(self):
        if self._home is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._home

    def test_adr_in_brain_decisions_is_indexed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, *_ = bootstrap.init(tmp)
            os.environ["AIES_HOME"] = str(root)
            d = root / "brain" / "decisions"
            d.mkdir(parents=True, exist_ok=True)
            (d / "ADR-0042-choice.md").write_text(
                "# ADR-0042: A choice\n- **Status:** Accepted\n", encoding="utf-8")
            refs = [it.ref for it in ADRProvider().catalog()]
            self.assertIn("ADR-0042-choice.md", refs)

    def test_brain_markdown_docs_are_surfaced_but_adrs_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, *_ = bootstrap.init(tmp)
            os.environ["AIES_HOME"] = str(root)
            brain = ProjectBrain()
            kdir = Path(brain.dir) / "knowledge"
            kdir.mkdir(parents=True, exist_ok=True)
            (kdir / "project-brief.md").write_text(
                "# Project Brief\nRequirements: multi-tenant, LGPD.", encoding="utf-8")
            (Path(brain.dir) / "adr").mkdir(parents=True, exist_ok=True)
            (Path(brain.dir) / "adr" / "ADR-0001-x.md").write_text(
                "# ADR-0001: x", encoding="utf-8")
            docs = [it for it in ProjectBrainProvider(brain).catalog()
                    if it.kind == "brain-doc"]
            self.assertTrue(any(it.title == "Project Brief" for it in docs),
                            "brain markdown doc not surfaced")
            self.assertFalse(any(it.ref.startswith("adr/") for it in docs),
                             "ADRs must not be surfaced as brain-doc")


if __name__ == "__main__":
    unittest.main()
