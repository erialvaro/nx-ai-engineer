"""Thin entrypoint shim — all CLI logic lives in nx_cli.orchestrator.

Works both in the repo (packages/ at the repo root) and after deployment via
init_aies.py (packages/ copied to .ai-project-assistant/packages/). It locates the engine
packages by walking up from this file until it finds a `packages/` dir holding
the nx_* packages, then delegates to nx_cli.orchestrator.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _base in _here.parents:
    _pk = _base / "packages"
    if _pk.is_dir() and any(_pk.glob("nx-*")):
        for _d in _pk.glob("nx-*"):
            if str(_d) not in sys.path:
                sys.path.insert(0, str(_d))
        break

from nx_cli.orchestrator import *  # noqa: E402,F401,F403
from nx_cli.orchestrator import build_parser, main, _make_adapter  # noqa: E402,F401

if __name__ == "__main__":
    raise SystemExit(main())
