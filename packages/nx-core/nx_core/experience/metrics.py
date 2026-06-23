"""Experience — usage metrics that let the framework learn from itself.

Subscribes to the event bus and records indicators (time, rework/retries,
failures, success, agent-selection precision, context reduction) to
`.ai-project/experience/`. Distinct from Observability (runtime plumbing):
Experience is the *aggregated, over-time* view used for continuous improvement.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..foundation import util


class ExperienceRecorder:
    # Events that carry signal worth aggregating.
    TRACKED = {
        "run.completed", "task.completed", "task.failed", "task.retrying",
        "agent.selected", "context.built", "review.completed", "delivery.completed",
    }

    def __init__(self, *, bus=None) -> None:
        self.counts: dict[str, int] = {}
        self._reductions: list[float] = []
        if bus is not None:
            self.attach(bus)

    def attach(self, bus) -> None:
        bus.subscribe("*", self._on_event)

    def _dir(self) -> Path:
        return util.ensure_dir(util.config_root() / "experience")

    def _on_event(self, event) -> None:
        if event.type not in self.TRACKED:
            return
        self.counts[event.type] = self.counts.get(event.type, 0) + 1
        if event.type == "context.built":
            self._reductions.append(float(event.payload.get("estimated_reduction", 0)))
        self._append(event)

    def _append(self, event) -> None:
        try:
            log = self._dir() / "events.jsonl"
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event.as_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass  # best-effort

    # -- KPIs ------------------------------------------------------------- #
    def summary(self) -> dict[str, Any]:
        completed = self.counts.get("task.completed", 0)
        failed = self.counts.get("task.failed", 0)
        retried = self.counts.get("task.retrying", 0)
        total = completed + failed
        avg_red = round(sum(self._reductions) / len(self._reductions), 4) if self._reductions else 0.0
        return {
            "runs": self.counts.get("run.completed", 0),
            "tasks_completed": completed,
            "tasks_failed": failed,
            "retries": retried,
            "success_rate": round(completed / total, 4) if total else None,
            "rework_rate": round(retried / total, 4) if total else None,
            "avg_context_reduction": avg_red,
            "reviews": self.counts.get("review.completed", 0),
            "deliveries": self.counts.get("delivery.completed", 0),
        }

    def persist_summary(self) -> Path:
        path = self._dir() / "summary.json"
        util.write_json(path, {**self.summary(), "generated_at": util.now_iso()})
        return path
