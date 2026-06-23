"""Telemetry — live counters and KPI snapshots derived from the event stream.

Observability is the runtime plumbing (counts now); Experience is the durable,
aggregated-over-time view. Telemetry exports a point-in-time snapshot to
`.ai-project/metrics/`.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from ..foundation import util


class Telemetry:
    def __init__(self, *, bus=None) -> None:
        self.counts: Counter = Counter()
        if bus is not None:
            self.attach(bus)

    def attach(self, bus) -> None:
        bus.subscribe("*", lambda e: self.counts.update([e.type]))

    def snapshot(self) -> dict[str, Any]:
        c = self.counts
        started = c.get("task.started", 0)
        completed = c.get("task.completed", 0)
        failed = c.get("task.failed", 0)
        return {
            "events_total": sum(c.values()),
            "by_type": dict(c),
            "kpis": {
                "tasks_started": started,
                "tasks_completed": completed,
                "tasks_failed": failed,
                "failure_rate": round(failed / started, 4) if started else None,
                "retries": c.get("task.retrying", 0),
                "runs": c.get("run.completed", 0),
                "deliveries": c.get("delivery.completed", 0),
            },
        }

    def export(self) -> Path:
        path = util.ensure_dir(util.config_root() / "metrics") / "telemetry.json"
        util.write_json(path, {**self.snapshot(), "generated_at": util.now_iso()})
        return path
