"""TaskGraph — the dependency-aware lifecycle of a set of nodes.

Builds the DAG from node dependencies, exposes which nodes are ready (all deps
COMPLETED and not blocked), detects cycles, and computes progress. It does not
execute anything — that is the Execution Engine's job.
"""
from __future__ import annotations

from typing import Iterable

from .domain import Node
from .states import ExecutionState


class CycleError(ValueError):
    pass


class TaskGraph:
    def __init__(self, nodes: Iterable[Node]) -> None:
        self.nodes: list[Node] = list(nodes)
        self._by_id = {n.id: n for n in self.nodes}
        self._validate_acyclic()

    # -- queries ---------------------------------------------------------- #
    def get(self, node_id: str) -> Node | None:
        return self._by_id.get(node_id)

    def deps(self, node: Node) -> list[Node]:
        return [self._by_id[d] for d in node.depends_on if d in self._by_id]

    def is_ready(self, node: Node) -> bool:
        if node.state not in (ExecutionState.PENDING, ExecutionState.BLOCKED,
                              ExecutionState.READY):
            return False
        return all(d.state == ExecutionState.COMPLETED for d in self.deps(node))

    def ready_nodes(self) -> list[Node]:
        # Includes nodes re-queued for retry (state READY); the executor moves
        # each to RUNNING immediately, so they are never double-scheduled within
        # an iteration.
        return [n for n in self.nodes if self.is_ready(n)]

    def pending_nodes(self) -> list[Node]:
        return [n for n in self.nodes
                if n.state not in (ExecutionState.COMPLETED, ExecutionState.SKIPPED,
                                   ExecutionState.CANCELLED, ExecutionState.FAILED)]

    def blocked_by(self, node: Node) -> list[Node]:
        """Deps that are not yet completed (why a node can't start)."""
        return [d for d in self.deps(node) if d.state != ExecutionState.COMPLETED]

    def is_done(self) -> bool:
        return all(n.state in (ExecutionState.COMPLETED, ExecutionState.SKIPPED,
                               ExecutionState.CANCELLED, ExecutionState.FAILED)
                   for n in self.nodes)

    def progress(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for n in self.nodes:
            counts[n.state.value] = counts.get(n.state.value, 0) + 1
        counts["total"] = len(self.nodes)
        return counts

    # -- internals -------------------------------------------------------- #
    def _validate_acyclic(self) -> None:
        WHITE, GREY, BLACK = 0, 1, 2
        color = {n.id: WHITE for n in self.nodes}

        def visit(nid: str) -> None:
            color[nid] = GREY
            for dep in self._by_id[nid].depends_on:
                if dep not in self._by_id:
                    continue
                if color[dep] == GREY:
                    raise CycleError(f"dependency cycle involving '{dep}'")
                if color[dep] == WHITE:
                    visit(dep)
            color[nid] = BLACK

        for n in self.nodes:
            if color[n.id] == WHITE:
                visit(n.id)
