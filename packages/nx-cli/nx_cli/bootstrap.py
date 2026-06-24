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

import re
import shutil
from pathlib import Path

CONFIG_DIRNAME = ".ai-project-assistant"
TEMPLATE = Path(__file__).resolve().parent / "_template"
# Project-foundation stack templates for `nxai new` (the scaffolding framework).
STACKS = Path(__file__).resolve().parent / "_stacks"

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


# --------------------------------------------------------------------------- #
# Project scaffolding (`nxai new`) — turn a stack template into a real project.
#
# A stack template lives under ``nx_cli/_stacks/<stack>/`` and is laid into a
# fresh project dir with two conventions:
#   • text content is rendered, replacing ``{{ variable }}`` tokens;
#   • a path part beginning ``dot.`` becomes a real dotfile (``dot.gitignore``
#     -> ``.gitignore``, ``dot.github`` -> ``.github``) — so dotfiles survive
#     packaging as wheel data, where leading-dot names are unreliable.
# Stdlib-only. No business logic is generated — only the cloud-agnostic
# foundation (Docker, env, adapters, observability hooks, docs).
# --------------------------------------------------------------------------- #

_VAR_RX = re.compile(r"\{\{\s*(\w+)\s*\}\}")
# Suffixes copied verbatim (never text-rendered).
_BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp",
                    ".woff", ".woff2", ".ttf", ".otf", ".pdf", ".zip"}


def stacks_dir() -> Path:
    """Absolute path to the bundled stack templates (ship as package data)."""
    return STACKS


def available_stacks() -> list[str]:
    """Names of bundled stacks (dirs under _stacks/ holding a stack.json)."""
    if not STACKS.is_dir():
        return []
    return sorted(d.name for d in STACKS.iterdir() if (d / "stack.json").is_file())


def render(text: str, variables: dict) -> str:
    """Replace ``{{ name }}`` tokens; unknown tokens are left untouched."""
    return _VAR_RX.sub(lambda m: str(variables.get(m.group(1), m.group(0))), text)


def _dotted(rel: Path) -> Path:
    """Map ``dot.`` path parts to real leading-dot names (packaging-safe)."""
    return Path(*[("." + part[4:]) if part.startswith("dot.") else part
                  for part in rel.parts])


def _render_tree(src: Path, dst: Path, variables: dict, force: bool) -> tuple[int, int]:
    copied = skipped = 0
    for p in sorted(src.rglob("*")):
        if p.is_dir() or "__pycache__" in p.parts or p.name.endswith(".pyc"):
            continue
        if p.name == "stack.json":  # metadata, not laid into the project
            continue
        dest = dst / _dotted(p.relative_to(src))
        if dest.exists() and not force:
            skipped += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix.lower() in _BINARY_SUFFIXES:
            shutil.copy2(p, dest)
        else:
            try:
                dest.write_text(render(p.read_text(encoding="utf-8"), variables),
                                encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(p, dest)
        copied += 1
    return copied, skipped


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return s or "app"


def scaffold_variables(name: str, extra: dict | None = None) -> dict:
    """The default render variables for a new project."""
    slug = _slug(name)
    variables = {
        "project_name": name,
        "project_slug": slug,
        "project_snake": slug.replace("-", "_"),
        "project_title": " ".join(w.capitalize() for w in slug.split("-")),
        "backend_port": "8000",
        "frontend_port": "3000",
    }
    if extra:
        variables.update(extra)
    return variables


def new_project(name: str, dest_parent, stack: str = "cloud-agnostic",
                variables: dict | None = None, force: bool = False
                ) -> tuple[Path, int, int]:
    """Create ``<dest_parent>/<name>/`` from a stack template. Returns (root,
    written, skipped). Refuses a non-empty target unless ``force``."""
    src = STACKS / stack
    if not (src / "stack.json").is_file():
        raise FileNotFoundError(
            f"unknown stack '{stack}'. Available: {', '.join(available_stacks()) or '—'}")
    root = Path(dest_parent).resolve() / name
    if root.exists() and any(root.iterdir()) and not force:
        raise FileExistsError(f"{root} already exists and is not empty (use --force)")
    root.mkdir(parents=True, exist_ok=True)
    return (root, *_render_tree(src, root, scaffold_variables(name, variables), force))
