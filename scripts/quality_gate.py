#!/usr/bin/env python
"""AIES Quality Gate — the platform's release/PR validation process.

A PR/release must NOT be approved if any gate fails:
  1. tests           — the full unittest suite passes
  2. import-cycles    — no circular imports in the `aies` package
  3. unused-imports   — no dead imports (excluding `__future__.annotations`)
  4. public-cli       — every expected CLI command is registered
  5. public-api       — legacy imports + SemVer version still resolve
  6. docs-present     — all required documents exist

Stdlib-only. Exit code 0 = all gates pass; non-zero = number of failed gates.
Run: `python scripts/quality_gate.py`
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TOOLS = SKILL / "framework" / "tools"
PACKAGES = SKILL / "packages"
# The deployable template (guides, agents, templates) ships as package data.
DOCS = PACKAGES / "nx-cli" / "nx_cli" / "_template" / "docs"


def _source_roots():
    """(scan_dir, name_base) pairs whose relative path yields the dotted module.

    Each `packages/nx-*` package is named relative to itself, so
    nx_core/foundation/util.py -> nx_core.foundation.util.
    """
    return [(d, d) for d in sorted(PACKAGES.glob("nx-*"))]


def _modname(path: Path, base: Path) -> str:
    rel = str(path.relative_to(base)).replace("\\", ".").replace("/", ".")[:-3]
    return rel[: -len(".__init__")] if rel.endswith(".__init__") else rel


# tests are fixtures; `_stacks`/`_template` are project templates (data shipped
# to scaffolded projects), NOT platform source — exclude from source scans.
_SKIP_PARTS = {"tests", "_stacks", "_template", "__pycache__"}


def _skip_path(p: Path) -> bool:
    return any(part in _SKIP_PARTS for part in p.parts)

REQUIRED_DOCS = [
    SKILL / "README.md", SKILL / "ROADMAP.md", SKILL / "CHANGELOG.md",
    SKILL / "CONTRIBUTING.md", SKILL / "CODE_OF_CONDUCT.md",
    SKILL / "RELEASE_NOTES.md",
    DOCS / "MIGRATION_GUIDE.md",
    DOCS / "SDK_GUIDE.md",
    DOCS / "PLUGIN_GUIDE.md",
    DOCS / "ENGINE_GUIDE.md",
    DOCS / "WORKFLOW_GUIDE.md",
    DOCS / "PROJECT_BRAIN.md",
    DOCS / "ARCHITECTURE_OVERVIEW.md",
    DOCS / "KNOWLEDGE_GUIDE.md",
    DOCS / "PROJECT_KNOWLEDGE.md",
    DOCS / "INSTALLER_GUIDE.md",
    DOCS / "UPGRADE_GUIDE.md",
    DOCS / "PACKS_GUIDE.md",
    DOCS / "PROVIDER_SDK_GUIDE.md",
    DOCS / "MARKETPLACE.md",
    DOCS / "ENGINEERING_CONTRACT.md",
    DOCS / "SCAFFOLDING_GUIDE.md",
    SKILL / "RELEASING.md",
]

EXPECTED_CLI = {
    "audit", "plan", "decide", "dispatch", "context", "run", "review",
    "deliver", "pipeline", "metrics", "insights", "recommend", "knowledge",
    "obsidian", "worktree", "tasks", "locks", "unlock", "status",
    "init", "update", "doctor", "docs", "version", "execute", "graph", "report", "pack",
    "scaffold", "contract", "new", "platform-audit",
}


def _ok(name: str, passed: bool, detail: str = "") -> bool:
    mark = "PASS" if passed else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    return passed


def gate_tests() -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-p", "test_*.py"],
        cwd=str(SKILL), capture_output=True, text=True)
    out = (proc.stderr or "") + (proc.stdout or "")
    passed = proc.returncode == 0 and "OK" in out
    ran = next((l for l in out.splitlines() if l.startswith("Ran ")), "")
    if not passed:
        # Surface the actual failures (so a CI failure is debuggable, not hidden).
        fails = [l for l in out.splitlines()
                 if l.startswith(("FAIL:", "ERROR:")) or "AssertionError" in l]
        for l in fails[:25]:
            print("        " + l)
    return _ok("tests", passed, ran)


def _imports(tree: ast.AST):
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name != "*" and a.name != "annotations":
                    yield (a.asname or a.name), n.lineno
        elif isinstance(n, ast.Import):
            for a in n.names:
                yield (a.asname or a.name).split(".")[0], n.lineno


def gate_unused_imports() -> bool:
    flagged = []
    for scan, base in _source_roots():
        for p in scan.rglob("*.py"):
            if _skip_path(p):
                continue
            src = p.read_text(encoding="utf-8")
            tree = ast.parse(src)
            used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            used |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
            all_names = _alls(tree)
            for name, ln in _imports(tree):
                # side-effect imports (e.g. workflow builtins) and re-exports are kept
                if name in used or name in all_names or _reexported(src, name):
                    continue
                flagged.append(f"{p.relative_to(base)}:{ln} '{name}'")
    return _ok("unused-imports", not flagged,
               "none" if not flagged else "; ".join(flagged[:6]))


def _alls(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(
                getattr(t, "id", "") == "__all__" for t in n.targets):
            if isinstance(n.value, (ast.List, ast.Tuple)):
                out |= {e.value for e in n.value.elts if isinstance(e, ast.Constant)}
    return out


def _reexported(src: str, name: str) -> bool:
    # Accept `from . import builtin  # noqa` style side-effect/re-export lines.
    return f"noqa" in src and name in src


def gate_cycles() -> bool:
    graph = {}
    for scan, base in _source_roots():
        for p in scan.rglob("*.py"):
            if _skip_path(p):
                continue
            mod = _modname(p, base)
            # current package: the module itself for an __init__, else its parent
            pkg_parts = (mod if p.name == "__init__.py" else
                         ".".join(mod.split(".")[:-1])).split(".")
            pkg_parts = [x for x in pkg_parts if x]
            tree = ast.parse(p.read_text(encoding="utf-8"))
            deps = set()
            for n in ast.walk(tree):
                if isinstance(n, ast.ImportFrom) and n.level:
                    keep = len(pkg_parts) - (n.level - 1)
                    bp = pkg_parts[:keep] if keep >= 0 else []
                    if n.module:
                        deps.add(".".join(bp + [n.module]))
                    else:  # `from . import X` -> the submodule pkg.X
                        for a in n.names:
                            deps.add(".".join(bp + [a.name]))
            graph[mod] = deps
    color, cycles = {}, []
    def visit(u, stack):
        color[u] = 1; stack.append(u)
        for v in graph.get(u, ()):
            if color.get(v) == 1:
                cycles.append(stack[stack.index(v):] + [v])
            elif color.get(v, 0) == 0 and v in graph:
                visit(v, stack)
        color[u] = 2; stack.pop()
    for m in list(graph):
        if color.get(m, 0) == 0:
            visit(m, [])
    return _ok("import-cycles", not cycles,
               "none" if not cycles else " / ".join(" -> ".join(c) for c in cycles[:3]))


def gate_cli() -> bool:
    sys.path.insert(0, str(TOOLS))
    try:
        import orchestrator
        parser = orchestrator.build_parser()
        registered = set()
        for action in parser._actions:
            if hasattr(action, "choices") and action.choices:
                registered |= set(action.choices)
        missing = EXPECTED_CLI - registered
        return _ok("public-cli", not missing,
                   "all present" if not missing else f"missing {sorted(missing)}")
    except Exception as exc:
        return _ok("public-cli", False, repr(exc))


def gate_public_api() -> bool:
    for d in PACKAGES.glob("nx-*"):
        sys.path.insert(0, str(d))
    try:
        import re
        import nx_core
        from nx_core import analyzer, planner  # noqa: F401
        import nx_sdk  # noqa: F401
        ok = bool(re.match(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?$", nx_core.__version__))
        return _ok("public-api", ok, f"version {nx_core.__version__}")
    except Exception as exc:
        return _ok("public-api", False, repr(exc))


def gate_docs() -> bool:
    missing = [d.name for d in REQUIRED_DOCS if not d.exists()]
    return _ok("docs-present", not missing,
               "all present" if not missing else f"missing {missing}")


def gate_py_floor() -> bool:
    """Builtin-generic annotations (list[…], dict[…]) are evaluated at runtime on
    Python 3.8 unless `from __future__ import annotations` is present — guard the
    declared 3.8 floor so this can't only fail on CI."""
    rx = re.compile(r"(:\s*|->\s*)(list|dict|set|tuple|frozenset|type)\[")
    flagged = []
    for base in (PACKAGES, SKILL / "tests", SKILL / "scripts"):
        for p in base.rglob("*.py"):
            if _skip_path(p):
                continue
            src = p.read_text(encoding="utf-8")
            if rx.search(src) and "from __future__ import annotations" not in src:
                flagged.append(str(p.relative_to(SKILL)))
    return _ok("py3.8-annotations", not flagged,
               "ok" if not flagged else f"missing __future__ import: {flagged[:5]}")


def main() -> int:
    print("AIES Quality Gate\n" + "=" * 40)
    gates = [gate_tests, gate_cycles, gate_unused_imports, gate_cli,
             gate_public_api, gate_docs, gate_py_floor]
    results = [g() for g in gates]
    failed = results.count(False)
    print("=" * 40)
    print(f"{'ALL GATES PASSED' if not failed else str(failed) + ' GATE(S) FAILED'}")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
