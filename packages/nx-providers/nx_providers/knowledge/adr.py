"""ADR Provider — structured knowledge from Architecture Decision Records.

Surfaces each ADR's number, title and status, and the cross-references between
ADRs (as relationships). It reads ADR metadata only; it does not interpret or
judge the decisions.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from nx_core.foundation import util
from .base import KnowledgeItem, KnowledgeProvider, Relationship, field_value, first_heading


class ADRProvider(KnowledgeProvider):
    name = "adr"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = (root or util.project_root()).resolve()
        self._items: Optional[list[KnowledgeItem]] = None

    def _dirs(self) -> list[Path]:
        cfg = util.config_root()
        return [
            self.root / "docs" / "adr",
            cfg / "docs" / "adr",
            cfg / "brain" / "adr",
            # `decisions` is also a Brain facet name; users naturally drop an ADR
            # there, so index it too (only ADR-*.md files match — no false hits).
            cfg / "brain" / "decisions",
            cfg / "knowledge" / "adr",
        ]

    def index(self) -> int:
        items: list[KnowledgeItem] = []
        seen: set[str] = set()
        for d in self._dirs():
            if not d.exists():
                continue
            for p in sorted(d.glob("ADR-*.md")):
                if p.name in seen:
                    continue
                seen.add(p.name)
                text = util.read_text(p)
                m = re.match(r"ADR-(\d+)", p.name)
                num = int(m.group(1)) if m else 0
                refs = {int(r) for r in re.findall(r"ADR-(\d{3,4})", text)}
                rels = [Relationship(f"adr:{num:04d}", f"adr:{r:04d}", "references")
                        for r in refs if r != num]
                items.append(KnowledgeItem(
                    id=f"adr:{num:04d}", provider=self.name, kind="adr", ref=p.name,
                    title=first_heading(text) or p.name,
                    metadata={"number": num, "status": field_value(text, "Status") or "Unknown"},
                    relationships=rels))
        items.sort(key=lambda it: it.metadata.get("number", 0))
        self._items = items
        return len(items)

    def catalog(self) -> list[KnowledgeItem]:
        if self._items is None:
            self.index()
        return self._items or []
