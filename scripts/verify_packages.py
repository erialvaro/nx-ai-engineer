#!/usr/bin/env python
"""Verify the monorepo package dependency graph is acyclic and matches the plan.

Two layers of checking:
  1. DECLARED graph — reads each `packages/<pkg>/pyproject.toml` `dependencies`,
     fails on an unknown dep, an up/sideways dep, or a cycle.
  2. REAL graph — AST-scans every module for absolute `nx_*` imports and fails if
     the actual cross-package imports form a cycle OR reference a package not in
     that package's declared `dependencies` (an undeclared edge). This catches the
     class of bug the declared-only check is blind to.
Stdlib-only. Wired into CI (.github/workflows/ci.yml).
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKGS = ROOT / "packages"

# The intended acyclic order (lower index may be depended on by higher).
EXPECTED_ORDER = [
    "nx-core", "nx-workflow", "nx-sdk", "nx-packs", "nx-providers",
    "nx-obsidian", "nx-knowledge", "nx-runtime", "nx-cli",
]


def _deps(pyproject: Path) -> list[str]:
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r"dependencies\s*=\s*\[([^\]]*)\]", text, re.S)
    if not m:
        return []
    # Accept an optional version specifier, e.g. "nx-core==1.0.0".
    return re.findall(r'"(nx-[a-z]+)[^"]*"', m.group(1))


def _real_imports(pkg_dir: Path, mod2pkg: dict[str, str]) -> set[str]:
    """The set of OTHER packages this package imports (absolute nx_* imports)."""
    self_pkg = pkg_dir.name
    edges: set[str] = set()
    for py in pkg_dir.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        names: set[str] = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                names.add(n.module.split(".")[0])
            elif isinstance(n, ast.Import):
                for a in n.names:
                    names.add(a.name.split(".")[0])
        for top in names:
            owner = mod2pkg.get(top)
            if owner and owner != self_pkg:
                edges.add(owner)
    return edges


def _acyclic(graph: dict[str, set[str]] | dict[str, list[str]]):
    color: dict[str, int] = {}
    cyc: list[list[str]] = []

    def visit(u: str, stack: list[str]) -> None:
        color[u] = 1
        stack.append(u)
        for v in graph.get(u, []):
            if color.get(v) == 1:
                cyc.append(stack[stack.index(v):] + [v])
            elif color.get(v, 0) == 0:
                visit(v, stack)
        color[u] = 2
        stack.pop()

    for p in graph:
        if color.get(p, 0) == 0:
            visit(p, [])
    return cyc


def main() -> int:
    if not PKGS.exists():
        print("no packages/ yet — nothing to verify")
        return 0
    graph: dict[str, list[str]] = {}
    for d in sorted(PKGS.iterdir()):
        pp = d / "pyproject.toml"
        if pp.exists():
            graph[d.name] = _deps(pp)

    problems = []
    rank = {p: i for i, p in enumerate(EXPECTED_ORDER)}
    for pkg, deps in graph.items():
        for dep in deps:
            if dep not in graph:
                problems.append(f"{pkg} depends on unknown package '{dep}'")
            elif rank.get(pkg, 99) <= rank.get(dep, 99):
                problems.append(f"{pkg} depends UP/sideways on '{dep}' (would risk a cycle)")

    # 1) Declared-graph cycle check.
    for c in _acyclic(graph):
        problems.append("DECLARED CYCLE: " + " -> ".join(c))

    # 2) Real-import check: the actual nx_* imports must be acyclic AND declared.
    #    module 'nx_core' lives in package 'nx-core' (underscore -> hyphen).
    mod2pkg = {f"nx_{d.name.split('-', 1)[1]}": d.name
               for d in PKGS.iterdir() if (d / "pyproject.toml").exists()}
    real: dict[str, set[str]] = {}
    for d in sorted(PKGS.iterdir()):
        if (d / "pyproject.toml").exists():
            real[d.name] = _real_imports(d, mod2pkg)
    for pkg, edges in real.items():
        declared = set(graph.get(pkg, []))
        for dep in sorted(edges - declared):
            problems.append(
                f"{pkg} IMPORTS '{dep}' but does not DECLARE it in pyproject "
                f"dependencies (undeclared edge)")
    for c in _acyclic(real):
        problems.append("REAL-IMPORT CYCLE: " + " -> ".join(c))

    print("Packages:", ", ".join(sorted(graph)))
    if problems:
        print("FAIL:")
        for p in problems:
            print("  -", p)
        return 1
    print("OK — declared + real-import graphs are acyclic and consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
