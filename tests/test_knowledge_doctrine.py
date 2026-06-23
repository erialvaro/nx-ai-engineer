"""Project Knowledge Engine — doctrine guardrails (enforced against real code).

The engine has EXACTLY five responsibilities (discover/index/relate/update/
deliver_context) and contains NO reasoning. All intelligence belongs to the
model; this layer only reduces its cognitive load. These tests enforce that the
`nx_knowledge/knowledge` layer never imports a reasoning/decision/memory layer,
so the doctrine cannot silently erode.
"""
import ast
import os
import tempfile
import unittest
from pathlib import Path

from nx_knowledge.knowledge.engine import KnowledgeEngine

# The actual knowledge layer in the monorepo.
KNOWLEDGE = (Path(__file__).resolve().parents[1]
             / "packages" / "nx-knowledge" / "nx_knowledge" / "knowledge")
KLAYER_PKG = "nx_knowledge.knowledge"

# Importing any of these (by dotted prefix) would mean the knowledge layer is
# reaching into reasoning/decision/memory — forbidden by ADR-0018.
FORBIDDEN_PREFIXES = (
    "nx_runtime",                # intelligence, schedulers, engines, adapters, pipeline
    "nx_sdk",                    # extension/registration surface
    "nx_core.kernel",            # execution kernel
    "nx_core.governance",
    "nx_core.observability",
    "nx_core.experience",
    "nx_knowledge.memory",       # operational memory (Brain) — injected, never imported
    "nx_knowledge.evolution",    # autonomous learning
)
# The layer may import only knowledge sources/primitives + the organizational view.
ALLOWED_PREFIXES = (
    "nx_core.foundation", "nx_core.util", "nx_core.config", "nx_core.agents",
    "nx_providers", "nx_obsidian", KLAYER_PKG,
)


def _nx_imports(path: Path) -> set[str]:
    """Every nx_* dotted module a file imports (absolute + resolved relative)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    pkg = KLAYER_PKG  # every file in this flat dir belongs to nx_knowledge.knowledge
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            if n.level == 0 and n.module and n.module.startswith("nx_"):
                out.add(n.module)
            elif n.level:  # relative -> resolve against this package
                base = pkg if n.level == 1 else ".".join(pkg.split(".")[:-(n.level - 1)])
                if n.module:
                    out.add(f"{base}.{n.module}")
                else:
                    for a in n.names:
                        out.add(f"{base}.{a.name}")
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("nx_"):
                    out.add(a.name)
    return out


class TestNoReasoningInKnowledge(unittest.TestCase):
    def test_layer_dir_exists(self):
        # Guard against the test silently scanning nothing (the failure mode of
        # the previous version).
        self.assertTrue(KNOWLEDGE.is_dir(), f"knowledge layer not found at {KNOWLEDGE}")
        self.assertTrue(list(KNOWLEDGE.glob("*.py")), "no python files scanned")

    def test_knowledge_layer_imports_no_reasoning(self):
        violations = []
        for p in KNOWLEDGE.rglob("*.py"):
            for mod in _nx_imports(p):
                if mod.startswith(FORBIDDEN_PREFIXES):
                    violations.append(f"{p.name} -> {mod}")
        self.assertEqual(violations, [], f"knowledge must not import reasoning layers: {violations}")

    def test_knowledge_layer_only_uses_allowed_packages(self):
        for p in KNOWLEDGE.rglob("*.py"):
            for mod in _nx_imports(p):
                self.assertTrue(
                    mod.startswith(ALLOWED_PREFIXES),
                    f"{p.name} imports unexpected nx module: {mod}")


class _Home:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        cfg = Path(self.tmp.name) / ".ai-project"
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


class TestFiveResponsibilities(unittest.TestCase):
    def test_exactly_the_five_responsibilities(self):
        self.assertEqual(KnowledgeEngine.RESPONSIBILITIES,
                         ("discover", "index", "relate", "update", "deliver_context"))

    def test_all_five_are_callable(self):
        with _Home():
            from nx_knowledge.memory.brain import ProjectBrain
            eng = KnowledgeEngine(ProjectBrain())
            self.assertIsInstance(eng.discover(), dict)        # 1 discover
            self.assertIsInstance(eng.index(), int)            # 2 index
            self.assertTrue(hasattr(eng.relate(), "nodes"))    # 3 relate (graph)
            self.assertIn("operational", eng.update())         # 4 update (sync)
            self.assertIsInstance(eng.deliver_context([]), dict)  # 5 deliver context

    def test_deliver_context_returns_only_data(self):
        # It delivers paths/labels (data) — never decisions or generated prose.
        with _Home():
            from nx_knowledge.memory.brain import ProjectBrain
            out = KnowledgeEngine(ProjectBrain()).deliver_context(["x.py"])
            self.assertIsInstance(out, dict)
            for v in out.values():
                self.assertTrue(all(isinstance(x, str) for x in v))


if __name__ == "__main__":
    unittest.main()
