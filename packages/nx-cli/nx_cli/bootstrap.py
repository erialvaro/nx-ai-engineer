"""Project bootstrap & maintenance for the `.ai-project-assistant/` working directory.

The platform code ships as installed packages; a project's `.ai-project-assistant/` holds
ONLY data + the deployable template assets. This module powers `nxai init`
(create/scaffold) and `nxai update` (refresh template assets, never user data).

Doctrine:
- The deployable template (agent specs, doc/code templates, project rules, the
  config example) ships as package data under ``nx_cli/_template/`` and is the
  single source of truth for what `init`/`update` lay down.
- `init` scaffolds the DATA dirs (brain/knowledge/obsidian/tasks/…) empty and
  seeds `config.json` from the example (only if absent).
- `update` refreshes ONLY the template-derived assets. It NEVER touches the
  user's `config.json`, Project Brain, Obsidian vault, knowledge, history, tasks,
  locks or reviews.
"""
from __future__ import annotations

import shutil
from pathlib import Path

CONFIG_DIRNAME = ".ai-project-assistant"
TEMPLATE = Path(__file__).resolve().parent / "_template"

# Template assets laid down on init AND refreshed on update
# (framework/SDK/providers/templates — never user data).
TEMPLATE_ASSETS = ("agents", "templates", "docs", "PROJECT_RULES.md")
# Data dirs scaffolded on init; NEVER overwritten on update.
DATA_DIRS = ("brain", "knowledge", "obsidian", "tasks", "locks", "reviews", "logs", "memory")
# User-owned paths that `update` must never overwrite.
PROTECTED = {"config.json", *DATA_DIRS}


def template_dir() -> Path:
    """Absolute path to the bundled deployable template (ships as package data)."""
    return TEMPLATE


def _copy_tree(src: Path, dst: Path, force: bool) -> tuple[int, int]:
    copied = skipped = 0
    for p in src.rglob("*"):
        if p.is_dir() or "__pycache__" in p.parts or p.name.endswith(".pyc"):
            continue
        dest = dst / p.relative_to(src)
        if dest.exists() and not force:
            skipped += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        copied += 1
    return copied, skipped


def _lay_assets(root: Path, force: bool) -> tuple[int, int]:
    copied = skipped = 0
    for asset in TEMPLATE_ASSETS:
        src = TEMPLATE / asset
        if src.is_dir():
            c, s = _copy_tree(src, root / asset, force)
            copied += c
            skipped += s
        elif src.is_file():
            dest = root / asset
            if dest.exists() and not force:
                skipped += 1
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                copied += 1
    # The config example is shipped for reference and refreshed by update.
    ex = TEMPLATE / "config.example.json"
    if ex.is_file():
        dest = root / "config.example.json"
        if force or not dest.exists():
            shutil.copy2(ex, dest)
            copied += 1
        else:
            skipped += 1
    return copied, skipped


def init(target, force: bool = False) -> tuple[Path, int, int]:
    """Create/scaffold `<target>/.ai-project-assistant/`. Returns (root, copied, skipped).

    Idempotent: existing files are preserved unless ``force`` is set. Always
    creates the empty DATA dirs and seeds `config.json` from the example if the
    project has none yet.
    """
    root = Path(target).resolve() / CONFIG_DIRNAME
    root.mkdir(parents=True, exist_ok=True)
    copied, skipped = _lay_assets(root, force)
    # Seed config.json from the example (never clobber an existing one).
    cfg = root / "config.json"
    if not cfg.exists():
        ex = TEMPLATE / "config.example.json"
        if ex.is_file():
            shutil.copy2(ex, cfg)
        else:
            cfg.write_text("{}\n", encoding="utf-8")
        copied += 1
    # Scaffold data dirs (empty, never seeded with code).
    for d in DATA_DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    return root, copied, skipped


def update(target) -> tuple[Path, int, int]:
    """Refresh template assets in an existing `.ai-project-assistant/` (force-overwrite).

    Updates only the framework/SDK/providers/templates assets + the config
    example. Never touches `config.json` or any data dir (Brain/Vault/Knowledge/
    history/tasks/locks/reviews). Returns (root, copied, skipped).
    """
    root = Path(target).resolve() / CONFIG_DIRNAME
    if not root.is_dir():
        raise FileNotFoundError(f"{root} not found — run `nxai init` first")
    return root, *_lay_assets(root, force=True)
