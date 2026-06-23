"""Markdown Provider — structured knowledge from Markdown documents.

Surfaces document structure: title, heading outline, word count and links to
other docs (as relationships). It parses Markdown *structure* only — never the
meaning of any code it might contain.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from nx_core.foundation import util
from .base import (
    SKIP_DIRS, KnowledgeItem, KnowledgeProvider, Relationship,
    first_heading, headings, md_links,
)


def _resolve(rel: str, link: str) -> str:
    link = link.split("#")[0].strip()
    if not link or link.startswith(("http://", "https://")):
        return ""
    base = Path(rel).parent
    return util.rel(base / link, Path(".")) if not link.startswith("/") else link.lstrip("/")


class MarkdownProvider(KnowledgeProvider):
    name = "markdown"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = (root or util.project_root()).resolve()
        self._items: Optional[list[KnowledgeItem]] = None

    def index(self) -> int:
        items: list[KnowledgeItem] = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
            for fn in filenames:
                if not fn.lower().endswith(".md"):
                    continue
                p = Path(dirpath) / fn
                rel = util.rel(p, self.root)
                text = util.read_text(p)
                hs = headings(text)
                rels = []
                for link in md_links(text):
                    if link.lower().endswith(".md"):
                        tgt = _resolve(rel, link)
                        if tgt:
                            rels.append(Relationship(f"md:{rel}", f"md:{tgt}", "links-to"))
                items.append(KnowledgeItem(
                    id=f"md:{rel}", provider=self.name, kind="doc", ref=rel,
                    title=first_heading(text) or fn,
                    metadata={"headings": hs[:10], "heading_count": len(hs),
                              "word_count": len(text.split())},
                    relationships=rels))
        self._items = items
        return len(items)

    def catalog(self) -> list[KnowledgeItem]:
        if self._items is None:
            self.index()
        return self._items or []
