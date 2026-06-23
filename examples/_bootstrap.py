"""Shared bootstrap for the Python examples.

Adds the in-repo nx_* packages to sys.path and points AIES_HOME at an isolated
temp `.ai-project` so examples never touch a real project. Import it first:

    from _bootstrap import aies_home  # noqa
"""
import os
import sys
import tempfile
from pathlib import Path

_PACKAGES = Path(__file__).resolve().parent.parent / "packages"
for _d in _PACKAGES.glob("nx-*"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

_tmp = tempfile.mkdtemp(prefix="aies-example-")
aies_home = Path(_tmp) / ".ai-project"
aies_home.mkdir(parents=True, exist_ok=True)
os.environ["AIES_HOME"] = str(aies_home)
