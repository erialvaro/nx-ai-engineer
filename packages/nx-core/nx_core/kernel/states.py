"""Execution state machine for task nodes.

Centralizes the legal transitions so no engine can move a node into an invalid
state. `transition()` validates and (optionally) emits `task.state_changed`.
"""
from __future__ import annotations

from enum import Enum


class ExecutionState(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


TERMINAL = {ExecutionState.COMPLETED, ExecutionState.SKIPPED, ExecutionState.CANCELLED}

# Legal transitions (mirrors §6.2 of the architecture document).
_ALLOWED: dict[ExecutionState, set[ExecutionState]] = {
    ExecutionState.PENDING: {ExecutionState.READY, ExecutionState.BLOCKED,
                             ExecutionState.CANCELLED, ExecutionState.SKIPPED},
    ExecutionState.READY: {ExecutionState.RUNNING, ExecutionState.CANCELLED,
                           ExecutionState.BLOCKED},
    ExecutionState.RUNNING: {ExecutionState.COMPLETED, ExecutionState.FAILED,
                             ExecutionState.CANCELLED},
    ExecutionState.BLOCKED: {ExecutionState.READY, ExecutionState.CANCELLED},
    ExecutionState.FAILED: {ExecutionState.RETRYING, ExecutionState.FAILED},
    ExecutionState.RETRYING: {ExecutionState.READY, ExecutionState.BLOCKED},
    ExecutionState.COMPLETED: set(),
    ExecutionState.SKIPPED: set(),
    ExecutionState.CANCELLED: set(),
}


class InvalidTransition(ValueError):
    pass


def can_transition(src: ExecutionState, dst: ExecutionState) -> bool:
    return dst in _ALLOWED.get(src, set())


def is_terminal(state: ExecutionState) -> bool:
    return state in TERMINAL


def transition(node, dst: ExecutionState, *, reason: str = "", bus=None) -> ExecutionState:
    """Move `node.state` to `dst` if legal, emit an event, return the new state.

    `node` is anything with a mutable `state` attribute and (optionally) `id`.
    """
    src: ExecutionState = node.state
    if src == dst:
        return dst
    if not can_transition(src, dst):
        raise InvalidTransition(f"{src.value} -> {dst.value} is not allowed")
    node.state = dst
    if bus is not None:
        node_id = getattr(node, "id", None) or getattr(node, "subtask_id", None)
        bus.emit("task.state_changed",
                 {"from": src.value, "to": dst.value, "reason": reason},
                 node_id=node_id)
    return dst
