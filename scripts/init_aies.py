#!/usr/bin/env python
"""Legacy bootstrap entrypoint — delegates to the official `nxai init` flow.

Kept for backward compatibility. The canonical way to initialize a project is now
the installed CLI:

    pip install nx-ai-engineer
    nxai init

This script reproduces `nxai init` from a source checkout (no install needed) by
putting the in-repo packages on sys.path and invoking the orchestrator.

Usage:
  python scripts/init_aies.py [TARGET_DIR] [--force] [--run-audit]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
for _d in (REPO_ROOT / "packages").glob("nx-*"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    target, force, run_audit = ".", False, False
    for a in argv:
        if a == "--force":
            force = True
        elif a == "--run-audit":
            run_audit = True
        elif not a.startswith("-"):
            target = a
    from nx_cli.orchestrator import main as cli
    args = ["init", target]
    if force:
        args.append("--force")
    if not run_audit:
        # The historical default was scaffold-only; keep it unless --run-audit.
        args.append("--no-audit")
    return cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
