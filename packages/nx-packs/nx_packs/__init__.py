"""nx_packs — Engineering Packs catalog (domain knowledge bundles).

An **Engineering Pack** is static engineering knowledge for a domain — its
documentation, architecture, patterns, templates, policies, ADRs, checklists,
examples and a distilled *context* file. A pack contains **no product code and no
AI**: it organizes domain knowledge so that *any* model applies it correctly.

The built-in catalog ships as package data. `nxai pack add <name>` installs a
pack into a project's `.ai-project-assistant/packs/<name>/`, where the Pack Provider
(`nx_providers.knowledge.packs`) catalogs it and the Context Builder feeds its
policies/checklists/context to the agents working in that domain.

Third parties can ship their own packs as separate packages following the same
`pack.json` + layout convention (the Marketplace / Provider SDK story).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

__version__ = "2.3.0"

CATALOG = Path(__file__).resolve().parent / "catalog"
# Files a pack feeds into agent context (the organizing surface).
CONTEXT_FILES = ("context.md", "policies.md", "checklists.md")
# Files every well-formed pack must contain.
REQUIRED = ("pack.json", "README.md", "context.md", "policies.md", "checklists.md")


def catalog() -> list[dict[str, Any]]:
    """All built-in pack manifests, sorted by name."""
    out: list[dict[str, Any]] = []
    if CATALOG.is_dir():
        for d in sorted(CATALOG.iterdir()):
            mf = d / "pack.json"
            if mf.is_file():
                out.append(json.loads(mf.read_text(encoding="utf-8")))
    return out


def names() -> list[str]:
    return [m["name"] for m in catalog()]


def pack_dir(name: str) -> Path:
    d = CATALOG / name
    if not (d / "pack.json").is_file():
        raise KeyError(f"unknown pack '{name}'")
    return d


def manifest(name: str) -> dict[str, Any]:
    return json.loads((pack_dir(name) / "pack.json").read_text(encoding="utf-8"))


def install(name: str, packs_root) -> Path:
    """Copy a catalog pack into `<packs_root>/<name>/`. Returns the install dir."""
    src = pack_dir(name)
    dst = Path(packs_root) / name
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc"):
            t = dst / p.relative_to(src)
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, t)
    return dst
