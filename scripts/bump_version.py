#!/usr/bin/env python
"""Release automation — set or check the version across the whole monorepo.

The version lives in every package `__init__` (`__version__`) and every
`pyproject.toml` (`version` + the pinned intra-workspace `dependencies`). This
script keeps all of them in lock-step.

    python scripts/bump_version.py --check        # verify every version agrees
    python scripts/bump_version.py 1.1.0          # set the new version everywhere

Stdlib-only. Run the Quality Gate after bumping, then tag `v<version>`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKGS = ROOT / "packages"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?$")


def _init_files() -> list[Path]:
    return [p for p in PKGS.glob("*/*/__init__.py")
            if re.search(r'__version__\s*=', p.read_text(encoding="utf-8"))]


def _pyprojects() -> list[Path]:
    return [ROOT / "pyproject.toml", *sorted(PKGS.glob("*/pyproject.toml"))]


def current_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in _init_files():
        m = re.search(r'__version__\s*=\s*"([^"]+)"', p.read_text(encoding="utf-8"))
        if m:
            out[str(p.relative_to(ROOT))] = m.group(1)
    for p in _pyprojects():
        m = re.search(r'^version\s*=\s*"([^"]+)"', p.read_text(encoding="utf-8"), re.M)
        if m:
            out[str(p.relative_to(ROOT))] = m.group(1)
    return out


def check() -> int:
    versions = current_versions()
    distinct = set(versions.values())
    if len(distinct) == 1:
        print(f"OK — all {len(versions)} version strings agree: {distinct.pop()}")
        return 0
    print("FAIL — version mismatch across the monorepo:")
    for f, v in sorted(versions.items()):
        print(f"  {v:14} {f}")
    return 1


def set_version(new: str) -> int:
    if not SEMVER.match(new):
        print(f"error: '{new}' is not a SemVer version (e.g. 1.1.0 or 1.1.0-rc1)", file=sys.stderr)
        return 2
    changed = 0
    for p in _init_files():
        t = p.read_text(encoding="utf-8")
        n = re.sub(r'(__version__\s*=\s*")[^"]+(")', rf'\g<1>{new}\g<2>', t)
        if n != t:
            p.write_text(n, encoding="utf-8"); changed += 1
    for p in _pyprojects():
        t = p.read_text(encoding="utf-8")
        n = re.sub(r'^(version\s*=\s*")[^"]+(")', rf'\g<1>{new}\g<2>', t, count=1, flags=re.M)
        # re-pin intra-workspace dependency specifiers
        n = re.sub(r'"(nx-[a-z]+)==[^"]+"', rf'"\g<1>=={new}"', n)
        if n != t:
            p.write_text(n, encoding="utf-8"); changed += 1
    print(f"set version {new} across {changed} file(s).")
    print("next: python scripts/quality_gate.py && git commit && git tag v" + new)
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--check":
        return check()
    return set_version(argv[0])


if __name__ == "__main__":
    raise SystemExit(main())
