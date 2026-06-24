"""Semantic Knowledge — prepared for future vector indexing / semantic search.

This ships the interfaces and a dependency-free `NullSemanticIndex` (keyword
fallback) so the platform can index and query architecture/decisions/patterns
today. A real embedding-based index can be registered later via the SDK without
changing any caller (architecture decision #8).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from nx_core.foundation import util


@dataclass
class Hit:
    doc_id: str
    score: float
    meta: dict[str, Any]


@runtime_checkable
class SemanticIndex(Protocol):
    def index(self, doc_id: str, text: str, meta: dict[str, Any] | None = None) -> None: ...
    def search(self, query: str, k: int = 5) -> list[Hit]: ...


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{3,}", (text or "").lower())}


class NullSemanticIndex:
    """Keyword-overlap index. Persists to `.ai-project-assistant/brain/knowledge/semantic.json`
    so it survives runs; swap for a vector index later via the SDK."""

    def __init__(self, persist: bool = False) -> None:
        self._docs: dict[str, dict[str, Any]] = {}
        self._persist = persist
        if persist:
            self._load()

    def _path(self):
        return util.config_root() / "brain" / "knowledge" / "semantic.json"

    def _load(self) -> None:
        self._docs = util.read_json(self._path(), {}) or {}

    def index(self, doc_id: str, text: str, meta: dict[str, Any] | None = None) -> None:
        self._docs[doc_id] = {"text": text, "meta": meta or {},
                              "tokens": sorted(_tokens(text))}
        if self._persist:
            util.write_json(self._path(), self._docs)

    def search(self, query: str, k: int = 5) -> list[Hit]:
        q = _tokens(query)
        if not q:
            return []
        hits = []
        for doc_id, doc in self._docs.items():
            toks = set(doc.get("tokens", []))
            overlap = len(q & toks)
            if overlap:
                score = overlap / len(q | toks)  # Jaccard
                hits.append(Hit(doc_id, round(score, 4), doc.get("meta", {})))
        hits.sort(key=lambda h: -h.score)
        return hits[:k]
