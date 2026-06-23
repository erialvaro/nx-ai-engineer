"""EventBus — in-process publish/subscribe (stdlib, synchronous).

The decoupling backbone: engines publish events; Governance, Observability,
Experience and Learning subscribe. Publishing never raises — a misbehaving
subscriber cannot break the run (its error is captured and re-published as a
`bus.handler_error` event for observability).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ..foundation import util

WILDCARD = "*"


@dataclass(frozen=True)
class Event:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    run_id: str | None = None
    node_id: str | None = None
    ts: str = field(default_factory=util.now_iso)

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.type, "ts": self.ts, "run_id": self.run_id,
            "node_id": self.node_id, "payload": self.payload,
        }


Handler = Callable[[Event], None]


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Handler]] = {}
        self._history: list[Event] = []

    def subscribe(self, event_type: str, handler: Handler) -> Handler:
        self._subs.setdefault(event_type, []).append(handler)
        return handler

    def publish(self, event: Event) -> Event:
        self._history.append(event)
        handlers = [*self._subs.get(event.type, []), *self._subs.get(WILDCARD, [])]
        for h in handlers:
            try:
                h(event)
            except Exception as exc:  # a subscriber must never break the run
                self._safe_emit_error(event, exc)
        return event

    def emit(self, event_type: str, payload: dict[str, Any] | None = None,
             *, run_id: str | None = None, node_id: str | None = None) -> Event:
        return self.publish(Event(event_type, payload or {}, run_id, node_id))

    def history(self, event_type: str | None = None) -> list[Event]:
        if event_type is None:
            return list(self._history)
        return [e for e in self._history if e.type == event_type]

    def _safe_emit_error(self, src: Event, exc: Exception) -> None:
        err = Event("bus.handler_error",
                    {"source_type": src.type, "error": repr(exc)},
                    src.run_id, src.node_id)
        self._history.append(err)
        for h in self._subs.get("bus.handler_error", []):
            try:
                h(err)
            except Exception:
                pass  # last line of defense: never raise from the bus


# A process-wide default bus is convenient for simple flows; engines that need
# isolation (e.g. tests) construct their own.
default_bus = EventBus()
