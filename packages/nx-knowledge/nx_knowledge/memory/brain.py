"""Project Brain — persistent project knowledge in specialized directories.

Replaces the monolithic `memory/architecture.json` with a directory-based store
(architecture decision #6). Each facet is its own directory of small JSON
records; `history` is append-only. The Brain stores **knowledge, never code**.
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Optional

from nx_core.foundation import util

FACETS = [
    "architecture", "modules", "services", "apis", "database", "workflows",
    "patterns", "history", "knowledge", "bugs", "decisions", "retrospectives", "adr",
    # Project Evolution facets (structured knowledge accrued after each run):
    "tests", "integrations", "dependencies", "lessons",
]

# Heuristic guard: refuse to store anything that looks like source code.
_CODE_SIGNALS = ("def ", "class ", "function ", "import ", "=>", "{\n", "};", "</")


def looks_like_code(value: Any) -> bool:
    """True if the value — or any string nested inside a list/dict — looks like
    source code. Recurses so code can't slip in inside a nested payload."""
    if isinstance(value, str):
        return sum(1 for s in _CODE_SIGNALS if s in value) >= 2 or len(value) > 4000
    if isinstance(value, dict):
        return any(looks_like_code(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(looks_like_code(v) for v in value)
    return False


def _sanitize(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if not looks_like_code(v)}


class ProjectBrain:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.dir = (root or util.config_root()) / "brain"

    def _facet(self, facet: str) -> Path:
        if facet not in FACETS:
            raise KeyError(f"unknown brain facet '{facet}'")
        return util.ensure_dir(self.dir / facet)

    # -- key/value facets ------------------------------------------------- #
    def put(self, facet: str, key: str, record: dict[str, Any]) -> None:
        path = self._facet(facet) / f"{util.slugify(key, 60)}.json"
        existing = util.read_json(path, {}) or {}
        merged = {**existing, **_sanitize(record), "_updated": util.now_iso()}
        util.write_json(path, merged)
        self._bump()

    def get(self, facet: str, key: Optional[str] = None) -> Any:
        d = self._facet(facet)
        if key is not None:
            return util.read_json(d / f"{util.slugify(key, 60)}.json", {}) or {}
        return {f.stem: util.read_json(f, {}) for f in sorted(d.glob("*.json"))}

    # -- append-only facets (history, retrospectives, bugs, decisions) ---- #
    def append(self, facet: str, record: dict[str, Any]) -> str:
        rec = {**_sanitize(record), "ts": util.now_iso(),
               "id": util.short_hash(util.now_iso() + repr(record) + uuid.uuid4().hex)}
        log = self._facet(facet) / "log.jsonl"
        with open(log, "a", encoding="utf-8") as fh:
            import json
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._bump()
        return rec["id"]

    def read_log(self, facet: str) -> list[dict[str, Any]]:
        log = self._facet(facet) / "log.jsonl"
        if not log.exists():
            return []
        import json
        out = []
        for line in util.read_text(log).splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return out

    def trim_log(self, facet: str, keep: int) -> int:
        """Keep only the last `keep` records of an append-only facet (used by the
        Brain Optimizer to bound growth). Returns how many were dropped."""
        records = self.read_log(facet)
        if len(records) <= keep:
            return 0
        kept = records[-keep:]
        import json
        log = self._facet(facet) / "log.jsonl"
        with open(log, "w", encoding="utf-8") as fh:
            for r in kept:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        self._bump()
        return len(records) - len(kept)

    # -- versioning ------------------------------------------------------- #
    def version(self) -> int:
        return (util.read_json(self.dir / "version.json", {"version": 0}) or {}).get("version", 0)

    def _bump(self) -> int:
        v = self.version() + 1
        util.write_json(self.dir / "version.json", {"version": v, "updated": util.now_iso()})
        return v

    # -- migration -------------------------------------------------------- #
    def migrate_legacy(self) -> bool:
        """Populate `architecture`/`patterns` from the old monolithic memory file,
        without deleting it. Idempotent."""
        legacy = util.read_json(util.config_root() / "memory" / "architecture.json", {})
        if not legacy:
            return False
        self.put("architecture", "current", {
            "stacks": legacy.get("stacks", []), "frameworks": legacy.get("frameworks", []),
            "is_monorepo": legacy.get("is_monorepo", False),
            "languages": legacy.get("languages", {}),
            "top_level_dirs": legacy.get("top_level_dirs", []),
        })
        for fw in legacy.get("frameworks", []):
            self.put("patterns", fw, {"name": fw, "source": "discovered"})
        return True
