"""Top-level test suite for nx-ai-engineer.

Importing this package bootstraps sys.path to the in-repo nx_* packages so the
tests resolve them without an install (each nx_* package also self-bootstraps,
but doing it here makes `python -m unittest discover -s tests -t .` work too).
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for _d in (_ROOT / "packages").glob("nx-*"):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))
