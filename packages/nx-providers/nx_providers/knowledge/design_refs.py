"""Design Reference matching — a knowledge-source primitive.

A **design reference** is a structured visual identity distilled from a real,
shipped website: its palette (light + dark tokens), type pairing, layout, mood and
the vertical it serves. Reference profiles ship as **data** in the
`design-references` Engineering Pack; this module is the **logic** that reads them
and matches one to a prompt.

It lives in the providers (knowledge-source) layer — not in the pack — so the
knowledge layer can use it without importing the pack catalog, and it stays pure
organization: it scores each reference against a prompt by **deterministic tag
overlap** (no embeddings, no model, no network). The aesthetic decision — which
reference to use and how to adapt it — belongs to the model; this only narrows the
field to references whose declared context actually appears in the prompt.

    prompt → normalize → tag overlap score → ranked references → (model designs)
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

# Fields every reference profile must declare (validated by tests + the CLI).
REQUIRED_FIELDS = ("id", "name", "vertical", "industry", "mood", "keywords",
                   "palette", "typography")
# Tag groups and how much a hit in each is worth. The vertical is the strongest
# signal (it names the kind of site); keywords carry the PT-BR/EN vocabulary.
TAG_WEIGHTS = {"vertical": 3.0, "industry": 2.0, "mood": 2.0, "keywords": 2.0}


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def tokenize(text: str) -> set[str]:
    """Lowercase, de-accent, split on non-alphanumerics → a set of word tokens.
    'Salão de Beleza' and 'salao beleza' both yield tokens {'salao','de','beleza'}."""
    norm = _strip_accents(str(text)).lower()
    return {t for t in re.split(r"[^a-z0-9]+", norm) if t}


def _term_tokens(term: str) -> list[str]:
    """A tag term may be multi-word ('design system') or a slug ('beauty-salon');
    both become the list of their component tokens."""
    return [t for t in re.split(r"[^a-z0-9]+", _strip_accents(str(term)).lower()) if t]


def score(prompt_tokens: set[str], entry: dict[str, Any]) -> float:
    """Weighted count of tag terms whose tokens all appear in the prompt.

    A multi-word term only scores when *every* one of its tokens is present, so
    'beauty' alone does not trigger the 'beauty salon' industry term but does
    match a bare 'beauty' keyword."""
    total = 0.0
    for field, weight in TAG_WEIGHTS.items():
        raw = entry.get(field)
        terms = [raw] if isinstance(raw, str) else list(raw or [])
        for term in terms:
            toks = _term_tokens(term)
            if toks and all(t in prompt_tokens for t in toks):
                total += weight
    return total


def match(prompt: str, entries: list[dict[str, Any]], *, k: int = 1,
          ) -> list[tuple[dict[str, Any], float]]:
    """Rank references by tag overlap with `prompt`; return the top `k` that score
    above zero, as (entry, score) pairs. Deterministic: ties break by `id` so the
    same prompt always yields the same order. Empty when nothing matches (the
    caller then lets the model choose, or injects nothing)."""
    toks = tokenize(prompt)
    scored = [(e, score(toks, e)) for e in entries]
    scored = [(e, s) for e, s in scored if s > 0]
    scored.sort(key=lambda es: (-es[1], str(es[0].get("id", ""))))
    return scored[: max(0, k)]


def load_references(references_dir: Path) -> list[dict[str, Any]]:
    """Load every ``*.json`` reference profile from a directory (skips the schema
    and any malformed file). Sorted by `id` for stable ordering."""
    out: list[dict[str, Any]] = []
    d = Path(references_dir)
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.json")):
        if p.name == "schema.json":
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict) and data.get("id"):
            out.append(data)
    out.sort(key=lambda e: str(e.get("id", "")))
    return out


def installed_references(packs_root: Path) -> list[dict[str, Any]]:
    """References from the installed `design-references` pack, if present."""
    return load_references(Path(packs_root) / "design-references" / "references")


def summarize(entry: dict[str, Any]) -> str:
    """A compact, model-facing brief for a reference — the text surfaced into the
    designer's Engineering Contract. Names the tokens; the model applies them."""
    pal = entry.get("palette", {}) or {}
    light = pal.get("light", {}) or {}
    typo = entry.get("typography", {}) or {}
    disp = (typo.get("display") or {}).get("family", "?")
    body = (typo.get("body") or {}).get("family", "?")
    roles = ", ".join(f"{k}:{v}" for k, v in light.items())
    lines = [
        f"design reference: {entry.get('name','?')} ({entry.get('id','?')})",
        f"  vertical: {entry.get('vertical','?')}  mood: {', '.join(entry.get('mood', []))}",
        f"  palette (light): {roles}",
        f"  type pairing: {disp} (display) + {body} (body)",
    ]
    if entry.get("layout"):
        lines.append(f"  layout: {entry['layout']}")
    if entry.get("source"):
        lines.append(f"  source: {entry['source']}")
    return "\n".join(lines)
