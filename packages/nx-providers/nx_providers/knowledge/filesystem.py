"""Filesystem Provider — structured knowledge about the project's files.

Surfaces file metadata (path, extension, language, owning agent, size) — it never
opens or interprets the code inside. This is the source the Context Engine uses
for its file list, so the Context Engine is no longer coupled to `os.walk`.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from nx_core import agents as agents_mod
from nx_core.foundation import util
from .base import LANG_BY_EXT, SKIP_DIRS, KnowledgeItem, KnowledgeProvider


class FilesystemProvider(KnowledgeProvider):
    name = "filesystem"

    def __init__(self, root: Optional[Path] = None, *, config: Optional[dict] = None,
                 limit: int = 5000) -> None:
        self.root = (root or util.project_root()).resolve()
        self.config = config or {}
        self.limit = limit
        self._items: Optional[list[KnowledgeItem]] = None

    # -- Context Engine conveniences ------------------------------------- #
    def paths(self) -> list[str]:
        return [it.ref for it in self.catalog()]

    def version(self) -> str:
        paths = self.paths()
        if util.is_git_repo(self.root):
            code, out, _ = util.git(["rev-parse", "HEAD"], self.root)
            if code == 0 and out:
                return out
        newest = 0.0
        for f in paths[:2000]:
            try:
                newest = max(newest, (self.root / f).stat().st_mtime)
            except OSError:
                pass
        return f"nogit-{int(newest)}-{len(paths)}"

    # -- provider contract ----------------------------------------------- #
    def index(self) -> int:
        reg = agents_mod.registry(self.config)
        items: list[KnowledgeItem] = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
            for fn in filenames:
                rel = util.rel(Path(dirpath) / fn, self.root)
                ext = Path(fn).suffix.lower()
                items.append(KnowledgeItem(
                    id=f"fs:{rel}", provider=self.name, kind="file", ref=rel, title=fn,
                    metadata={
                        "ext": ext, "language": LANG_BY_EXT.get(ext, ""),
                        "top_dir": rel.split("/")[0] if "/" in rel else ".",
                        "owner_agent": agents_mod.route_file(rel, reg),
                    }))
                if len(items) >= self.limit:
                    self._items = items
                    return len(items)
        self._items = items
        return len(items)

    def catalog(self) -> list[KnowledgeItem]:
        if self._items is None:
            self.index()
        return self._items or []

    def enrich(self, item: KnowledgeItem) -> KnowledgeItem:
        try:
            item.metadata.setdefault("size_bytes", (self.root / item.ref).stat().st_size)
        except OSError:
            pass
        return item
