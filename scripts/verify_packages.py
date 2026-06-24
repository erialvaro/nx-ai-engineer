#!/usr/bin/env python
"""Verify the monorepo package dependency graph is acyclic and matches the plan.

The graph is keyed by **distribution name** (the PyPI `name`, e.g. `nxai-core`),
which is decoupled from the directory (`packages/nx-core`) and the import module
(`nx_core`).

Two layers of checking:
  1. DECLARED graph — reads each package's `dependencies`, fails on an unknown dep,
     an up/sideways dep, or a cycle.
  2. REAL graph — AST-scans every module for absolute `nx_*` imports, maps each to
     its distribution, and fails if the real cross-package imports form a cycle OR
     reference a distribution not in that package's declared `dependencies`.
Stdlib-only. Wired into CI (.github/workflows/ci.yml).
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKGS = ROOT / "packages"

# Intended acyclic order by DISTRIBUTION name (lower may be depended on by higher).
EXPECTED_ORDER = [
    "nxai-core", "nxai-workflow", "nxai-sdk", "nxai-packs", "nxai-providers",
    "nxai-obsidian", "nxai-knowledge", "nxai-runtime", "nxai-cli",
]


def _name(pyproject: Path) -> str:
    m = re.search(r'^name\s*=\s*"([^"]+)"', pyproject.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else pyproject.parent.name


def _deps(pyproject: Path) -> list[str]:
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r"dependencies\s*=\s*\[([^\]]*)\]", text, re.S)
    if not m:
        return []
    # Intra-workspace deps, with an optional version specifier (e.g. "nxai-core==1.0.0").
    return re.findall(r'"(nxai-[a-z]+)[^"]*"', m.group(1))


def _module(pkg_dir: Path) -> str | None:
    """The importable top-level module shipped by a package (e.g. nx_core)."""
    for init in pkg_dir.glob("nx_*/__init__.py"):
        return init.parent.name
    return None


def _real_imports(pkg_dir: Path, self_dist: str, mod2dist: dict[str, str]) -> set[str]:
    """Distributions this package imports (resolved from absolute nx_* imports)."""
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
            owner = mod2dist.get(top)
            if owner and owner != self_dist:
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
    pkgs = [d for d in sorted(PKGS.iterdir()) if (d / "pyproject.toml").exists()]
    dist = {d: _name(d / "pyproject.toml") for d in pkgs}
    graph: dict[str, list[str]] = {dist[d]: _deps(d / "pyproject.toml") for d in pkgs}
    mod2dist = {m: dist[d] for d in pkgs if (m := _module(d))}

    problems = []
    rank = {p: i for i, p in enumerate(EXPECTED_ORDER)}
    for pkg, deps in graph.items():
        for dep in deps:
            if dep not in graph:
                problems.append(f"{pkg} depends on unknown package '{dep}'")
            elif rank.get(pkg, 99) <= rank.get(dep, 99):
                problems.append(f"{pkg} depends UP/sideways on '{dep}' (would risk a cycle)")

    for c in _acyclic(graph):
        problems.append("DECLARED CYCLE: " + " -> ".join(c))

    # Real-import check (by distribution name).
    real: dict[str, set[str]] = {dist[d]: _real_imports(d, dist[d], mod2dist) for d in pkgs}
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
