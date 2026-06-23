"""Git Provider — structured knowledge from version control.

Surfaces commit metadata (hash, author, date, subject) and the set of changed
files. It never reads or interprets the content/diff of the code.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from nx_core.foundation import util
from .base import KnowledgeItem, KnowledgeProvider, Relationship

_SEP = "\x1f"


class GitProvider(KnowledgeProvider):
    name = "git"

    def __init__(self, root: Optional[Path] = None, *, max_commits: int = 20,
                 base: str = "HEAD") -> None:
        self.root = (root or util.project_root()).resolve()
        self.max_commits = max_commits
        self.base = base
        self._items: Optional[list[KnowledgeItem]] = None

    def index(self) -> int:
        items: list[KnowledgeItem] = []
        if util.is_git_repo(self.root):
            code, out, _ = util.git(
                ["log", f"-{self.max_commits}", f"--pretty=%H{_SEP}%an{_SEP}%ad{_SEP}%s",
                 "--date=short"], self.root)
            if code == 0 and out:
                for line in out.splitlines():
                    parts = line.split(_SEP)
                    if len(parts) == 4:
                        h, author, date, subject = parts
                        items.append(KnowledgeItem(
                            id=f"git:{h[:10]}", provider=self.name, kind="commit",
                            ref=h[:10], title=subject,
                            metadata={"author": author, "date": date}))
            for f in util.changed_files(self.base, self.root):
                items.append(KnowledgeItem(
                    id=f"git-change:{f}", provider=self.name, kind="change",
                    ref=f, title=f, metadata={"status": "changed", "base": self.base},
                    relationships=[Relationship(f"git-change:{f}", f"fs:{f}", "same-as")]))
        self._items = items
        return len(items)

    def catalog(self) -> list[KnowledgeItem]:
        if self._items is None:
            self.index()
        return self._items or []
