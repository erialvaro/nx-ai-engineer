"""Lock Engine — cooperative file locking across concurrent agents/tasks.

Locks live as one JSON file per logical lock under `.ai-project-assistant/locks/`.
They are advisory: agents (human or AI) consult them before claiming files so
two parallel tasks don't fight over the same code. Nothing enforces them at the
filesystem level — the value is visibility, surfaced in every task report.
"""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

from . import util


def _locks_dir() -> Path:
    return util.ensure_dir(util.config_root() / "locks")


def all_locks() -> list[dict[str, Any]]:
    out = []
    for f in sorted(_locks_dir().glob("*.json")):
        data = util.read_json(f, {})
        if data:
            data["_file"] = f.name
            out.append(data)
    return out


def active_locks() -> list[dict[str, Any]]:
    return [l for l in all_locks() if l.get("status", "active") == "active"]


def conflicts_for(paths: list[str], owner_task: str | None = None) -> list[dict[str, Any]]:
    """Return active locks held by *other* tasks that cover any of `paths`."""
    hits = []
    for lock in active_locks():
        if owner_task and lock.get("task") == owner_task:
            continue
        locked = lock.get("path", "")
        for p in paths:
            if p == locked or fnmatch.fnmatch(p, locked) or fnmatch.fnmatch(locked, p):
                hits.append({**lock, "requested": p})
                break
    return hits


def acquire(path: str, task: str, owner: str, status: str = "active") -> dict[str, Any]:
    key = util.short_hash(f"{task}:{path}")
    lock = {
        "id": key,
        "path": path,
        "task": task,
        "owner": owner,
        "status": status,
        "acquired_at": util.now_iso(),
    }
    util.write_json(_locks_dir() / f"{key}.json", lock)
    return lock


def release(task: str | None = None, path: str | None = None) -> int:
    """Mark matching locks released. Returns count released."""
    n = 0
    for lock in all_locks():
        if task and lock.get("task") != task:
            continue
        if path and lock.get("path") != path:
            continue
        if lock.get("status") == "active":
            lock["status"] = "released"
            lock["released_at"] = util.now_iso()
            lock.pop("_file", None)
            util.write_json(_locks_dir() / f"{lock['id']}.json", lock)
            n += 1
    return n
