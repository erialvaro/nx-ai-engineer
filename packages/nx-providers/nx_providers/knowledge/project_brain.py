"""Project Brain Provider — structured knowledge stored in the Project Brain.

Surfaces what the platform has already learned (patterns, per-workflow stats,
recent retrospectives) as knowledge items. The Brain is injected (duck-typed:
needs `get`, `read_log`) so this layer never imports the Memory layer — keeping
the dependency direction acyclic (Memory consumes Knowledge, not the reverse).

It only surfaces stored knowledge; it never re-derives or interprets it.
"""
from __future__ import annotations

from typing import Any

from .base import KnowledgeItem, KnowledgeProvider


class ProjectBrainProvider(KnowledgeProvider):
    name = "project-brain"

    def __init__(self, brain: Any) -> None:
        # `brain` is any object exposing get(facet, key=None) and read_log(facet).
        self.brain = brain
        self._items = None

    def index(self) -> int:
        items: list[KnowledgeItem] = []

        # Patterns.
        for key in ("recurring-agent-sets", "failure-prone-agents", "hot-areas"):
            rec = self._safe_get("patterns", key)
            if rec:
                items.append(KnowledgeItem(
                    id=f"brain:pattern:{key}", provider=self.name, kind="brain-pattern",
                    ref=key, title=key,
                    metadata={k: v for k, v in rec.items() if k != "_updated"}))

        # Per-workflow success statistics.
        for name, stats in (self._safe_get("workflows") or {}).items():
            if isinstance(stats, dict):
                items.append(KnowledgeItem(
                    id=f"brain:workflow:{name}", provider=self.name, kind="brain-workflow",
                    ref=name, title=f"workflow:{name}",
                    metadata={k: v for k, v in stats.items() if k != "_updated"}))

        # Recent retrospectives (summaries only — no code).
        for r in self._safe_log("retrospectives")[-10:]:
            items.append(KnowledgeItem(
                id=f"brain:retro:{r.get('id', '?')}", provider=self.name, kind="brain-retro",
                ref=str(r.get("id", "")), title=str(r.get("request", ""))[:60],
                metadata={"status": r.get("status"), "workflow": r.get("workflow"),
                          "agents": r.get("agents_used"), "success": r.get("strategy_success")}))

        self._items = items
        return len(items)

    def catalog(self) -> list[KnowledgeItem]:
        if self._items is None:
            self.index()
        return self._items or []

    # -- defensive accessors (brain may be empty/partial) ---------------- #
    def _safe_get(self, facet: str, key: str | None = None):
        try:
            return self.brain.get(facet, key) if key is not None else self.brain.get(facet)
        except Exception:
            return {} if key is None else None

    def _safe_log(self, facet: str):
        try:
            return self.brain.read_log(facet)
        except Exception:
            return []
