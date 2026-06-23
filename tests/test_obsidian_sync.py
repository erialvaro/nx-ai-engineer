"""Obsidian Sync — visual representation of the Project Brain (auto, incremental).

The vault uses the official numbered structure (00 Dashboard … 14 Retrospectives).
"""
import os
import tempfile
import unittest
from pathlib import Path

from nx_obsidian.knowledge.obsidian_sync import CATEGORIES, VAULT, ObsidianSync
from nx_knowledge.memory.brain import ProjectBrain
from nx_core.observability.events import EventBus

_FOLDER = {title: folder for folder, title in VAULT}


def note(vault: Path, title: str) -> Path:
    """Resolve a category note to its numbered-folder path."""
    return vault / _FOLDER[title] / f"{title}.md"


class _Home:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        cfg = Path(self.tmp.name) / ".ai-project"
        (cfg / "docs" / "adr").mkdir(parents=True)
        (cfg / "docs" / "adr" / "ADR-0001-a.md").write_text(
            "# ADR-0001: Use OAuth\n- **Status:** Accepted\nrelated ADR-0002\n", encoding="utf-8")
        (cfg / "docs" / "adr" / "ADR-0002-b.md").write_text(
            "# ADR-0002: Tokens\n- **Status:** Accepted\n", encoding="utf-8")
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
    brain.put("architecture", "current", {"stacks": ["Python"], "frameworks": ["FastAPI"]})
    brain.put("services", "auth", {"path": "api/auth"})
    brain.append("retrospectives", {"request": "Implement OAuth", "status": "done",
                                     "workflow": "full-dev", "agents_used": ["backend"],
                                     "failures": 1, "retries": 1, "strategy_success": True})


class TestRender(unittest.TestCase):
    def test_every_category_in_numbered_folder(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            s = ObsidianSync(b); s.sync()
            for c in CATEGORIES:
                self.assertTrue(note(s.vault, c).exists(), f"missing {c}")
            # the 15 official folders exist
            for folder, _title in VAULT:
                self.assertTrue((s.vault / folder).is_dir(), f"missing folder {folder}")
            self.assertTrue((s.vault / "00 Dashboard" / "Relationships.md").exists())

    def test_dashboard_links_every_category(self):
        with _Home():
            s = ObsidianSync(ProjectBrain()); s.sync()
            dash = note(s.vault, "Dashboard").read_text(encoding="utf-8")
            for c in CATEGORIES:
                if c == "Dashboard":
                    continue
                self.assertIn(f"[[{c}]]", dash)
            self.assertIn("[[Relationships]]", dash)

    def test_adr_notes_have_backlinks(self):
        with _Home():
            s = ObsidianSync(ProjectBrain()); s.sync()
            adr1 = s.vault / "02 ADR" / "ADR-0001.md"
            self.assertTrue(adr1.exists())
            self.assertIn("[[ADR-0002]]", adr1.read_text(encoding="utf-8"))
            self.assertIn("[[ADR-0001]]", note(s.vault, "ADRs").read_text(encoding="utf-8"))

    def test_relationship_map_has_mermaid(self):
        with _Home():
            s = ObsidianSync(ProjectBrain()); s.sync()
            rel = (s.vault / "00 Dashboard" / "Relationships.md").read_text(encoding="utf-8")
            self.assertIn("```mermaid", rel)
            self.assertIn("ADR0001", rel)

    def test_reflects_brain_not_invents(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            s = ObsidianSync(b); s.sync()
            self.assertIn("auth", note(s.vault, "Services").read_text(encoding="utf-8"))
            self.assertIn("Implement OAuth", note(s.vault, "Features").read_text(encoding="utf-8"))


class TestIncremental(unittest.TestCase):
    def test_unchanged_data_writes_nothing(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            s = ObsidianSync(b)
            first = s.sync()
            self.assertGreater(first["written"], 0)
            second = s.sync()
            self.assertEqual(second["written"], 0)
            self.assertEqual(second["unchanged"], first["total"])

    def test_change_rewrites_only_affected(self):
        with _Home():
            b = ProjectBrain(); _seed(b)
            s = ObsidianSync(b); s.sync()
            b.put("services", "billing", {"path": "api/billing"})
            rep = s.sync()
            self.assertGreater(rep["written"], 0)
            self.assertLess(rep["written"], rep["total"])  # incremental, not full

    def test_manifest_tracks_only_generated_notes(self):
        with _Home():
            s = ObsidianSync(ProjectBrain()); s.sync()
            (s.vault / "My Note.md").write_text("mine", encoding="utf-8")
            s.sync()
            self.assertTrue((s.vault / "My Note.md").exists())


class TestAutoSync(unittest.TestCase):
    def test_syncs_on_pipeline_completed(self):
        with _Home():
            bus = EventBus()
            s = ObsidianSync(ProjectBrain(), bus=bus)
            bus.emit("pipeline.completed", {"request": "x"})
            self.assertTrue(note(s.vault, "Dashboard").exists())
            self.assertEqual(len(bus.history("obsidian.synced")), 1)

    def test_disabled_by_config(self):
        with _Home():
            bus = EventBus()
            s = ObsidianSync(ProjectBrain(), config={"obsidian_sync": False}, bus=bus)
            bus.emit("pipeline.completed", {"request": "x"})
            self.assertFalse(note(s.vault, "Dashboard").exists())


class TestNoDuplication(unittest.TestCase):
    def test_adr_notes_link_source_not_copy_body(self):
        with _Home():
            s = ObsidianSync(ProjectBrain()); s.sync()
            note_txt = (s.vault / "02 ADR" / "ADR-0001.md").read_text(encoding="utf-8")
            self.assertIn("Source:", note_txt)
            self.assertNotIn("## Context", note_txt)  # ADR body sections not duplicated


if __name__ == "__main__":
    unittest.main()
