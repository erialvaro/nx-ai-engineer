"""BaseEngine — the contract every AIES engine obeys, including the MANDATORY
execution-mode progression Dry Run -> Test -> Execute (architecture decision #2).

No engine may perform real changes (`EXECUTE`) for a given context until it has
successfully completed `DRY_RUN` and `TEST` for that same context within the
current cycle. The gate lives in `run()` and is enforced for all subclasses, so
it cannot be bypassed by individual engines.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from ..foundation import util


class ExecutionMode(str, Enum):
    DRY_RUN = "dry_run"   # simulate; zero side effects; returns the planned actions
    TEST = "test"         # validate in a safe/sandbox manner; no production effect
    EXECUTE = "execute"   # real effect — only after DRY_RUN + TEST passed


# Required order; EXECUTE requires all predecessors to have passed.
_REQUIRED_BEFORE = {
    ExecutionMode.DRY_RUN: [],
    ExecutionMode.TEST: [ExecutionMode.DRY_RUN],
    ExecutionMode.EXECUTE: [ExecutionMode.DRY_RUN, ExecutionMode.TEST],
}


@dataclass
class EngineResult:
    mode: ExecutionMode
    ok: bool
    actions: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value, "ok": self.ok, "actions": self.actions,
            "diagnostics": self.diagnostics, "error": self.error,
        }


class ModeGateError(RuntimeError):
    """Raised when EXECUTE/TEST is attempted before its prerequisites passed."""


def _ctx_key(ctx: Any) -> str:
    try:
        return util.short_hash(json.dumps(ctx, sort_keys=True, default=str))
    except TypeError:
        return util.short_hash(repr(ctx))


class BaseEngine(ABC):
    """Subclass and implement the three modes. Always call `run(ctx, mode)` (not
    the mode methods directly) so the gate is enforced and events are emitted.
    """

    name: str = "engine"

    def __init__(self, *, bus=None) -> None:
        self._bus = bus
        # Tracks which modes passed per context key, for the current cycle.
        self._passed: dict[str, set[ExecutionMode]] = {}

    # -- subclasses implement these -------------------------------------- #
    @abstractmethod
    def dry_run(self, ctx: Any) -> EngineResult: ...

    @abstractmethod
    def test(self, ctx: Any) -> EngineResult: ...

    @abstractmethod
    def execute(self, ctx: Any) -> EngineResult: ...

    # -- the enforced entrypoint ----------------------------------------- #
    def run(self, ctx: Any, mode: ExecutionMode = ExecutionMode.DRY_RUN) -> EngineResult:
        key = _ctx_key(ctx)
        passed = self._passed.setdefault(key, set())

        missing = [m for m in _REQUIRED_BEFORE[mode] if m not in passed]
        if missing:
            names = ", ".join(m.value for m in missing)
            raise ModeGateError(
                f"engine '{self.name}': mode '{mode.value}' requires {names} to pass first"
            )

        self._emit(f"engine.{mode.value}", {"engine": self.name, "phase": "start"})
        if mode is ExecutionMode.DRY_RUN:
            result = self.dry_run(ctx)
        elif mode is ExecutionMode.TEST:
            result = self.test(ctx)
        else:
            result = self.execute(ctx)

        if result.ok:
            passed.add(mode)
        self._emit(f"engine.{mode.value}",
                   {"engine": self.name, "phase": "end", "ok": result.ok})
        return result

    def run_full_cycle(self, ctx: Any) -> EngineResult:
        """Convenience: DRY_RUN -> TEST -> EXECUTE, stopping on first failure."""
        for mode in (ExecutionMode.DRY_RUN, ExecutionMode.TEST, ExecutionMode.EXECUTE):
            result = self.run(ctx, mode)
            if not result.ok:
                return result
        return result

    # -- helpers ---------------------------------------------------------- #
    def _emit(self, event_type: str, payload: dict[str, Any]) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, payload)


class ReadOnlyEngine(BaseEngine):
    """Base for analysis engines (Audit/Review/…) that never mutate anything.

    The same analysis satisfies all three modes, so they trivially pass the gate
    while remaining safe. Subclasses implement `analyze(ctx) -> EngineResult`.
    """

    @abstractmethod
    def analyze(self, ctx: Any) -> EngineResult: ...

    def dry_run(self, ctx: Any) -> EngineResult:
        return self.analyze(ctx)

    def test(self, ctx: Any) -> EngineResult:
        return self.analyze(ctx)

    def execute(self, ctx: Any) -> EngineResult:
        return self.analyze(ctx)
