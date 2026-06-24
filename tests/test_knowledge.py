"""Knowledge Providers — base contract, the 6 providers, registry, context wiring."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from nx_knowledge.knowledge import (
    ADRProvider, FilesystemProvider, GitProvider, KnowledgeItem, KnowledgeProvider,
    KnowledgeRegistry, MarkdownProvider, ObsidianProvider, ProjectBrainProvider,
    Relationship, default_registry,
)
from nx_providers.knowledge.base import score_scope


class _Project:
    """A throwaway project with files, markdown, ADRs, an obsidian vault, git."""
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = Path(self.tmp.name)
        (r / "apps/api/services").mkdir(parents=True)
        (r / "docs/adr").mkdir(parents=True)
        (r / "vault/.obsidian").mkdir(parents=True)
        (r / "apps/api/services/auth.py").write_text("x=1\n", encoding="utf-8")
        (r / "README.md").write_text("# Project\nSee [auth](docs/auth.md).\n", encoding="utf-8")
        (r / "docs/auth.md").write_text("# Auth\n## Flow\ndetails\n", encoding="utf-8")
        (r / "docs/adr/ADR-0001-use-oauth.md").write_text(
            "# ADR-0001: Use OAuth\n- **Status:** Accepted\nrelated to ADR-0002.\n", encoding="utf-8")
        (r / "docs/adr/ADR-0002-tokens.md").write_text(
            "# ADR-0002: Tokens\n- **Status:** Accepted\n", encoding="utf-8")
        (r / "vault/note.md").write_text("# Note\nlinks [[Other]] #security #auth\n", encoding="utf-8")
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.email=a@b.c", "-c", "user.name=t", "commit", "-qm", "init"]):
            subprocess.run(["git", *args], cwd=r, capture_output=True)
        (r / ".ai-project-assistant").mkdir()
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(r / ".ai-project-assistant")
        self.root = r
        return r

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        try:
            self.tmp.cleanup()
        except (PermissionError, OSError):
            pass


class TestBaseContract(unittest.TestCase):
    def test_item_and_relationship_serialize(self):
        it = KnowledgeItem("id", "p", "file", "a.py", "a",
                           relationships=[Relationship("a", "b", "links-to")])
        d = it.as_dict()
        self.assertEqual(d["relationships"][0]["kind"], "links-to")

    def test_score_scope_filters_and_orders(self):
        it = KnowledgeItem("i", "p", "doc", "docs/auth.md", "Auth flow")
        self.assertIsNotNone(score_scope(it, {"query": "auth"}))
        self.assertIsNone(score_scope(it, {"query": "billing"}))
        self.assertIsNone(score_scope(it, {"areas": ["apps/"]}))


class TestFilesystemProvider(unittest.TestCase):
    def test_catalog_and_paths(self):
        with _Project() as r:
            p = FilesystemProvider(r)
            self.assertGreater(p.index(), 0)
            self.assertIn("apps/api/services/auth.py", p.paths())
            item = next(i for i in p.catalog() if i.ref.endswith("auth.py"))
            self.assertEqual(item.kind, "file")
            self.assertEqual(item.metadata["language"], "Python")
            self.assertTrue(item.metadata["owner_agent"])

    def test_version_uses_git_head(self):
        with _Project() as r:
            self.assertEqual(len(FilesystemProvider(r).version()), 40)  # a git sha

    def test_is_provider(self):
        self.assertIsInstance(FilesystemProvider(), KnowledgeProvider)


class TestGitProvider(unittest.TestCase):
    def test_commits_catalogued(self):
        with _Project() as r:
            items = GitProvider(r).catalog()
            self.assertTrue(any(i.kind == "commit" for i in items))
            commit = next(i for i in items if i.kind == "commit")
            self.assertIn("author", commit.metadata)


class TestMarkdownProvider(unittest.TestCase):
    def test_title_headings_and_links(self):
        with _Project() as r:
            items = MarkdownProvider(r).catalog()
            readme = next(i for i in items if i.ref == "README.md")
            self.assertEqual(readme.title, "Project")
            self.assertTrue(any(rel.kind == "links-to" for rel in readme.relationships))
            auth = next(i for i in items if i.ref.endswith("docs/auth.md"))
            self.assertIn("Flow", auth.metadata["headings"])


class TestADRProvider(unittest.TestCase):
    def test_number_status_and_refs(self):
        with _Project() as r:
            items = ADRProvider(r).catalog()
            self.assertEqual(len(items), 2)
            a1 = items[0]
            self.assertEqual(a1.metadata["number"], 1)
            self.assertEqual(a1.metadata["status"], "Accepted")
            self.assertTrue(any(rel.target == "adr:0002" for rel in a1.relationships))


class TestObsidianProvider(unittest.TestCase):
    def test_wikilinks_and_tags(self):
        with _Project() as r:
            items = ObsidianProvider(r).catalog()  # auto-detects vault/.obsidian
            self.assertTrue(items)
            note = items[0]
            self.assertIn("security", note.metadata["tags"])
            self.assertTrue(any(rel.kind == "wikilink" for rel in note.relationships))

    def test_no_vault_is_graceful(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ObsidianProvider(Path(d)).index(), 0)


class TestProjectBrainProvider(unittest.TestCase):
    def test_surfaces_brain_knowledge(self):
        with _Project():
            from nx_knowledge.memory.brain import ProjectBrain
            brain = ProjectBrain()
            brain.put("patterns", "recurring-agent-sets", {"sets": [{"agents": ["backend"]}]})
            brain.put("workflows", "full-dev", {"runs": 2, "successes": 2, "success_rate": 1.0})
            items = ProjectBrainProvider(brain).catalog()
            kinds = {i.kind for i in items}
            self.assertIn("brain-pattern", kinds)
            self.assertIn("brain-workflow", kinds)


class TestRegistry(unittest.TestCase):
    def test_default_registry_has_all_providers(self):
        with _Project():
            from nx_knowledge.memory.brain import ProjectBrain
            reg = default_registry(brain=ProjectBrain())
            self.assertEqual(set(reg.names()),
                             {"filesystem", "git", "markdown", "adr", "obsidian",
                              "packs", "project-brain"})

    def test_index_all_and_retrieve(self):
        with _Project():
            reg = default_registry()
            counts = reg.index_all()
            self.assertGreater(counts["filesystem"], 0)
            hits = reg.retrieve({"query": "auth"}, providers=["markdown", "adr"])
            self.assertTrue(hits)
            self.assertTrue(all(h.provider in ("markdown", "adr") for h in hits))

    def test_aggregate_relationships(self):
        with _Project():
            rels = default_registry().relationships()
            self.assertTrue(any(r.kind == "links-to" for r in rels))


class TestContextUsesProviders(unittest.TestCase):
    def test_context_sources_files_via_provider(self):
        with _Project():
            from nx_core.kernel.domain import Subtask
            from nx_knowledge.memory.context import ContextBuilder
            res = ContextBuilder().build(
                agent="backend",
                subtask=Subtask(id="backend", agent="backend",
                                objective="implement auth service", areas=["apps/api"]),
                use_cache=False)
            self.assertIn("apps/api/services/auth.py", res.context.files)
            self.assertGreater(res.total_files, 0)
            # docs enriched from the Markdown/ADR providers:
            self.assertTrue(any(d.endswith(".md") for d in res.context.docs))


if __name__ == "__main__":
    unittest.main()
