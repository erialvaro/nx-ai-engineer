"""Knowledge Providers — base contract.

A Knowledge Provider supplies **structured knowledge** to the platform. No
knowledge source may be coupled directly to the Context Engine: everything flows
through a provider.

A provider's ONLY responsibilities are to:
  - index      (build/refresh its catalog)
  - catalog    (list what it knows, as structured items)
  - retrieve   (return items relevant to a scope)
  - enrich     (add metadata to an item)
  - relationships (relate items to each other)

A provider MUST NEVER:
  - make decisions          (that is the Decision/Intelligence layer)
  - interpret code          (it surfaces metadata/paths, not parsed semantics)
  - generate answers        (it returns data, not prose)

So a provider is a pure, read-only knowledge source. Stdlib-only.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

# Directories never scanned by file-based providers.
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
    ".next", ".nuxt", "out", "target", "coverage", ".terraform", ".idea",
    ".vscode", ".ai-project-assistant", "vendor", ".cache", ".pytest_cache", ".mypy_cache",
}

LANG_BY_EXT = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
    ".rb": "Ruby", ".php": "PHP", ".cs": "C#", ".sql": "SQL", ".vue": "Vue",
    ".svelte": "Svelte", ".ex": "Elixir", ".dart": "Dart", ".md": "Markdown",
}


@dataclass
class Relationship:
    source: str
    target: str
    kind: str  # links-to, references, wikilink, tagged, in-dir, changed-in …

    def as_dict(self) -> dict[str, str]:
        return {"source": self.source, "target": self.target, "kind": self.kind}


@dataclass
class KnowledgeItem:
    id: str
    provider: str
    kind: str                 # file, commit, change, doc, adr, note, brain-*
    ref: str                  # path or identifier
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "provider": self.provider, "kind": self.kind,
            "ref": self.ref, "title": self.title, "metadata": self.metadata,
            "relationships": [r.as_dict() for r in self.relationships],
        }


def score_scope(item: KnowledgeItem, scope: dict[str, Any]) -> Optional[int]:
    """Pure retrieval relevance: count of query tokens / area matches. Returns
    None if the item does not match the (non-empty) filters. Ordering only — the
    provider does NOT decide anything beyond presence."""
    query = (scope.get("query") or "").lower()
    areas = scope.get("areas") or []
    hay = " ".join([item.ref, item.title, " ".join(map(str, item.metadata.values()))]).lower()

    score = 0
    if query:
        tokens = [t for t in re.findall(r"[a-z0-9]{3,}", query)]
        hits = sum(1 for t in set(tokens) if t in hay)
        if not hits:
            return None
        score += hits
    if areas:
        base = [str(a).rstrip("/*") for a in areas if str(a).rstrip("/*")]
        if base and not any(b in item.ref for b in base):
            return None
        score += 1
    return score


class KnowledgeProvider(ABC):
    name: str = "provider"

    @abstractmethod
    def index(self) -> int:
        """(Re)build the catalog. Returns the number of items."""

    @abstractmethod
    def catalog(self) -> list[KnowledgeItem]:
        """All known items (builds the index on first call)."""

    def retrieve(self, scope: Optional[dict[str, Any]] = None) -> list[KnowledgeItem]:
        """Items relevant to `scope` ({query, areas, limit}). Pure filter + order."""
        scope = scope or {}
        scored = []
        for it in self.catalog():
            s = score_scope(it, scope)
            if s is not None:
                scored.append((s, it))
        scored.sort(key=lambda x: (-x[0], x[1].ref))
        items = [it for _, it in scored]
        limit = scope.get("limit")
        return items[:limit] if limit else items

    def enrich(self, item: KnowledgeItem) -> KnowledgeItem:
        """Add metadata to an item. Default: no-op."""
        return item

    def relationships(self) -> list[Relationship]:
        rels: list[Relationship] = []
        for it in self.catalog():
            rels.extend(it.relationships)
        return rels


# --------------------------------------------------------------------------- #
# Small text helpers shared by markdown/adr/obsidian providers (structural only)
# --------------------------------------------------------------------------- #
def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def headings(text: str) -> list[str]:
    return [ln.lstrip("#").strip() for ln in text.splitlines() if ln.lstrip().startswith("#")]


def md_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)


def field_value(text: str, name: str) -> str:
    m = re.search(rf"\*\*{re.escape(name)}:\*\*\s*([^\n]+)", text)
    return m.group(1).strip() if m else ""
