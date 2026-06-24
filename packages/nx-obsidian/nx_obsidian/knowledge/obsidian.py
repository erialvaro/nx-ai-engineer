"""Obsidian Provider — structured knowledge from an Obsidian vault.

Surfaces notes with their tags and `[[wikilinks]]` (as relationships). The vault
path comes from `config.json > obsidian_vault`, or is auto-detected by looking for
a `.obsidian` folder. If there is no vault, the catalog is simply empty.

It parses note structure (tags/links) only — never code semantics.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from nx_core.foundation import util
from nx_providers.knowledge.base import SKIP_DIRS, KnowledgeItem, KnowledgeProvider, Relationship, first_heading

_WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
_TAG = re.compile(r"(?:^|\s)#([A-Za-z0-9_/-]{2,})")


def default_vault(config: Optional[dict] = None) -> Path:
    """Where the generated vault lives: `config.obsidian_vault` or, by default,
    `.ai-project-assistant/obsidian/` (a self-contained vault that travels with the project)."""
    v = (config or {}).get("obsidian_vault")
    if v:
        return Path(v).expanduser()
    return util.config_root() / "obsidian"


class ObsidianProvider(KnowledgeProvider):
    name = "obsidian"

    def __init__(self, root: Optional[Path] = None, *, vault: Optional[str] = None,
                 config: Optional[dict] = None) -> None:
        self.root = (root or util.project_root()).resolve()
        cfg = config or {}
        if vault:
            self.vault: Optional[Path] = Path(vault)
        elif cfg.get("obsidian_vault"):
            self.vault = Path(cfg["obsidian_vault"]).expanduser()
        else:
            # Prefer the project-local generated vault; else auto-detect a vault.
            local = self.root / ".ai-project-assistant" / "obsidian"
            self.vault = local if local.exists() else self._detect()
        self._items: Optional[list[KnowledgeItem]] = None

    def _detect(self) -> Optional[Path]:
        for dirpath, dirnames, _ in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
            if ".obsidian" in dirnames:
                return Path(dirpath)
        return None

    def index(self) -> int:
        items: list[KnowledgeItem] = []
        if self.vault and self.vault.exists():
            paths = list(self.vault.rglob("*.md"))
            # Resolve `[[wikilinks]]` (which use a note's name) to the real note
            # ref/id, so the relationship graph actually connects (not dangling).
            by_name: dict[str, str] = {}
            for p in paths:
                rel = util.rel(p, self.vault)
                by_name.setdefault(rel, rel)
                by_name.setdefault(Path(rel).stem, rel)
            for p in paths:
                rel = util.rel(p, self.vault)
                text = util.read_text(p)
                tags = sorted({t for t in _TAG.findall(text)})
                links = _WIKILINK.findall(text)
                rels = []
                for ln in links:
                    name = ln.split("|")[0].strip()
                    target = by_name.get(name) or by_name.get(Path(name).stem, name)
                    rels.append(Relationship(f"obs:{rel}", f"obs:{target}", "wikilink"))
                items.append(KnowledgeItem(
                    id=f"obs:{rel}", provider=self.name, kind="note", ref=rel,
                    title=first_heading(text) or p.stem,
                    metadata={"tags": tags, "wikilinks": len(links)},
                    relationships=rels))
        self._items = items
        return len(items)

    def catalog(self) -> list[KnowledgeItem]:
        if self._items is None:
            self.index()
        return self._items or []
