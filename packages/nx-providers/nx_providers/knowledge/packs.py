"""Pack Provider — surfaces installed Engineering Packs as structured knowledge.

An Engineering Pack is domain knowledge (policies, checklists, patterns, context)
installed under `.ai-project-assistant/packs/<name>/`. This provider catalogs each installed
pack so the Context Engine can enrich an agent's context with the relevant
domain's policies/checklists — exactly like any other Knowledge Provider.

It only **organizes** (catalogs/retrieves) — it never decides or interprets code.
It reads installed pack data; it does not depend on the pack catalog package.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from nx_core.foundation import util
from .base import KnowledgeItem, KnowledgeProvider, Relationship, first_heading


def _bullets(text: str) -> list[str]:
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("- "):
            out.append(s[2:].strip().lstrip("[ ] ").strip())
    return out


class PackProvider(KnowledgeProvider):
    name = "packs"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or util.config_root()
        self._items: Optional[list[KnowledgeItem]] = None

    @property
    def packs_dir(self) -> Path:
        return self.root / "packs"

    def index(self) -> int:
        self._items = self._scan()
        return len(self._items)

    def catalog(self) -> list[KnowledgeItem]:
        if self._items is None:
            self._items = self._scan()
        return self._items

    def _scan(self) -> list[KnowledgeItem]:
        items: list[KnowledgeItem] = []
        d = self.packs_dir
        if not d.is_dir():
            return items
        for pack in sorted(p for p in d.iterdir() if (p / "pack.json").is_file()):
            try:
                mf: dict[str, Any] = json.loads((pack / "pack.json").read_text(encoding="utf-8"))
            except Exception:
                continue
            policies = _read(pack / "policies.md", _bullets)
            checklist = _read(pack / "checklists.md", _bullets)
            context = _read(pack / "context.md", lambda t: t)
            name = mf.get("name", pack.name)
            item = KnowledgeItem(
                id=f"pack:{name}", provider=self.name, kind="pack",
                ref=str(pack / "context.md"),
                title=mf.get("title", name),
                metadata={
                    "name": name, "domain": mf.get("domain", ""),
                    "category": mf.get("category", ""),
                    "summary": mf.get("summary", ""), "tags": mf.get("tags", []),
                    "status": mf.get("status", ""),
                    "policies": policies, "checklists": checklist,
                    "context": (context or first_heading(context or "")),
                    # Engineering-Contract fields (declarative — what the pack requires).
                    "applies_to": mf.get("applies_to", []),
                    "required_adrs": mf.get("required_adrs", []),
                    "mandatory_tests": mf.get("mandatory_tests", []),
                    "validations": mf.get("validations", []),
                    "brain_facets": mf.get("brain_facets", []),
                },
                relationships=[Relationship(f"pack:{name}", f"domain:{mf.get('domain', '')}", "applies-to")],
            )
            items.append(item)
        return items


def _read(path: Path, fn):
    try:
        return fn(path.read_text(encoding="utf-8"))
    except Exception:
        return [] if fn is _bullets else ""
