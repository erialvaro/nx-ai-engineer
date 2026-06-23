#!/usr/bin/env python
"""NX AI Engineer — source-checkout installer.

The supported way to install the platform is via PyPI:

    pip install nx-ai-engineer
    nxai init

This script exists only for running from a **source checkout** (no install): it
delegates to `scripts/init_aies.py`, which puts the in-repo packages on the path
and runs the official `nxai init` flow into a target project's `.ai-project/`.

Usage:
  python installer/install.py <target-project> [--force] [--run-audit]
"""
import runpy
import sys
from pathlib import Path

_INIT = Path(__file__).resolve().parent.parent / "scripts" / "init_aies.py"

if __name__ == "__main__":
    if not _INIT.exists():
        print("error: scripts/init_aies.py not found", file=sys.stderr)
        raise SystemExit(2)
    sys.argv = [str(_INIT), *sys.argv[1:]]
    runpy.run_path(str(_INIT), run_name="__main__")
