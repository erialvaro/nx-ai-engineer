"""AgentAdapter — the only boundary between the core and an AI model/CLI.

The Execution Engine receives an adapter by injection and never imports a
specific provider. Swapping models = swapping adapters; the core is untouched.

Adapters MAY accept an optional `mode` (Dry Run → Test → Execute) so they can
behave safely per phase. It is optional and keyword-only: the framework passes
it **only** to adapters that declare it (see `schedulers.execution.adapter_runner`),
so simpler adapters keeping the 3-argument signature remain fully compatible.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from nx_core.kernel.domain import AgentContext, AgentResult
from nx_core.kernel.engine import ExecutionMode

__all__ = ["AgentAdapter", "AgentContext", "AgentResult", "ExecutionMode"]


@runtime_checkable
class AgentAdapter(Protocol):
    name: str

    def run(self, *, agent: str, context: AgentContext, instructions: str,
            mode: "ExecutionMode" = ExecutionMode.EXECUTE) -> AgentResult:
        """Execute one agent's work for a subtask and report the outcome.

        `mode` is optional; adapters that don't support phases may omit it.
        """
        ...
