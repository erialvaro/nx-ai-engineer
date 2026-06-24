"""ADR engine — auto-generates Architecture Decision Records.

Governance listens for decision events and writes an ADR to the Project Brain
(`.ai-project-assistant/brain/adr/`, falling back to `.ai-project-assistant/knowledge/adr/`). ADRs
are knowledge, never code. The numbering is monotonic and gap-free.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from ..foundation import util


def adr_dir() -> Path:
    root = util.config_root()
    brain = root / "brain" / "adr"
    # Prefer the dir-based Brain location; fall back to knowledge/adr.
    return brain if brain.exists() else root / "knowledge" / "adr"


def next_number(directory: Optional[Path] = None) -> int:
    directory = directory or adr_dir()
    if not directory.exists():
        return 1
    nums = []
    for f in directory.glob("ADR-*.md"):
        m = re.match(r"ADR-(\d+)", f.name)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def render(number: int, title: str, *, context: str, decision: str,
           alternatives: list[str] | None = None,
           consequences: list[str] | None = None, status: str = "Accepted") -> str:
    L = [
        f"# ADR-{number:04d}: {title}",
        "",
        f"- **Status:** {status}",
        f"- **Date:** {util.today()}",
        "",
        "## Context", context, "",
        "## Decision", decision, "",
        "## Alternatives considered",
    ]
    for a in (alternatives or ["—"]):
        L.append(f"- {a}")
    L += ["", "## Consequences"]
    for c in (consequences or ["—"]):
        L.append(f"- {c}")
    L.append("")
    return "\n".join(L)


def create(title: str, *, context: str, decision: str,
           alternatives: list[str] | None = None,
           consequences: list[str] | None = None,
           directory: Optional[Path] = None) -> dict[str, Any]:
    directory = directory or adr_dir()
    util.ensure_dir(directory)
    number = next_number(directory)
    slug = util.slugify(title, 50)
    path = directory / f"ADR-{number:04d}-{slug}.md"
    content = render(number, title, context=context, decision=decision,
                     alternatives=alternatives, consequences=consequences)
    util.write_text(path, content)
    return {"number": number, "path": str(path), "title": title}


def subscribe(bus) -> None:
    """Attach to an EventBus so `*.decided` events become ADRs automatically."""
    def handler(event):
        p = event.payload or {}
        if not p.get("title"):
            return
        info = create(p["title"], context=p.get("context", ""),
                      decision=p.get("decision", ""),
                      alternatives=p.get("alternatives"),
                      consequences=p.get("consequences"))
        bus.emit("adr.created", {"number": info["number"], "title": info["title"]})
    bus.subscribe("decision.recorded", handler)
