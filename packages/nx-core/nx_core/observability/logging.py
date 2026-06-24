"""Structured logging — every event as one JSON line under `.ai-project-assistant/logs/`.

A pure event subscriber; attaching/removing it changes nothing in the domain
engines. Logs are append-only and machine-readable.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..foundation import util


class EventLogger:
    def __init__(self, *, bus=None, filename: str = "events.jsonl") -> None:
        self._filename = filename
        self._count = 0
        if bus is not None:
            self.attach(bus)

    def attach(self, bus) -> None:
        bus.subscribe("*", self._on_event)

    def _path(self) -> Path:
        return util.ensure_dir(util.config_root() / "logs") / self._filename

    def _on_event(self, event) -> None:
        try:
            with open(self._path(), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event.as_dict(), ensure_ascii=False) + "\n")
            self._count += 1
        except OSError:
            pass  # logging is best-effort; never break a run

    @property
    def written(self) -> int:
        return self._count
