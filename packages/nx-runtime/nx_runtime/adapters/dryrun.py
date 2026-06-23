"""DryRunAdapter — the safe default. Performs no work and changes nothing; it
simply reports success so the Execution Engine can exercise the full pipeline
(scheduling, states, retries, progress) without touching project code.

This is what guarantees AIES never mutates a codebase unless a real adapter is
explicitly injected.
"""
from __future__ import annotations

from nx_core.kernel.domain import AgentContext, AgentResult


class DryRunAdapter:
    name = "dry-run"

    def __init__(self, *, fail_agents: set[str] | None = None) -> None:
        # `fail_agents` lets tests simulate failures deterministically.
        self._fail = fail_agents or set()

    def run(self, *, agent: str, context: AgentContext, instructions: str,
            mode=None) -> AgentResult:
        # `mode` is accepted for forward-compatibility and ignored: a dry-run
        # adapter never has side effects in any mode.
        if agent in self._fail:
            return AgentResult(ok=False, error=f"simulated failure for '{agent}'")
        return AgentResult(ok=True, notes=f"[dry-run] would execute '{agent}': {instructions}")
