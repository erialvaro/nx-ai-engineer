"""Context cache with version-based invalidation.

The cache key embeds a `version` (git HEAD, or a file-mtime signature when not a
repo). When the project changes, the version changes, so a stale entry simply
can never be hit — invalidation is by construction. `clear()` prunes old files.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from nx_core.foundation import util


def cache_dir() -> Path:
    return util.ensure_dir(util.config_root() / "context-cache")


def make_key(agent: str, subtask_id: str, objective: str, version: str) -> str:
    return util.short_hash(f"{agent}|{subtask_id}|{objective}|{version}", 12)


def read(key: str) -> Optional[dict[str, Any]]:
    return util.read_json(cache_dir() / f"{key}.json", None)


def write(key: str, data: dict[str, Any]) -> None:
    util.write_json(cache_dir() / f"{key}.json", data)


def clear() -> int:
    n = 0
    d = cache_dir()
    for f in d.glob("*.json"):
        try:
            f.unlink()
            n += 1
        except OSError:
            pass
    return n
