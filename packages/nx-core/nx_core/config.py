"""Configuration loading.

Config lives at `.ai-project-assistant/config.json` and is fully optional — every value
has a sane default so the framework works the moment the folder is copied in.
Projects override only what they need (extra agents, custom domain rules,
protected paths, branch prefix, etc.).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import util

DEFAULTS: dict[str, Any] = {
    "project_name": None,            # auto-detected if null
    "branch_prefix": "feature",      # worktree branches -> feature/<agent>
    "default_base": "HEAD",          # diff base for review
    "large_file_loc": 400,           # review flags files larger than this
    # Domain rules let the framework enforce project-specific invariants
    # (e.g. multi-tenant isolation, LGPD/PII). Empty = generic project.
    "domain_rules": [],              # list of free-text rules surfaced to agents
    # Paths no agent may modify, regardless of role (glob-relative to root).
    "protected_paths": [],
    # Extra custom agents merged on top of the built-in registry.
    "extra_agents": {},
    # Override or disable built-in agents by name.
    "disabled_agents": [],
    # Obsidian: auto-sync a visual vault from the Project Brain (knowledge view).
    "obsidian_sync": True,
    "obsidian_vault": None,   # path; null => .ai-project-assistant/obsidian
    # Auto-record: ON by default. From the moment `.ai-project-assistant` exists at
    # the project root, every knowledge-producing command (plan/execute/run/
    # deliver) automatically persists to the Project Brain and syncs the vault —
    # recording is ambient and never needs an explicit `nxai knowledge sync`.
    "auto_record": True,
    # Knowledge Engine: opt-in commit of brain+obsidian to Git (historical memory).
    "knowledge_git_snapshot": False,
    # Engineering Contracts: per-agent overrides for pack auto-application, e.g.
    # {"backend": {"packs": ["billing"], "exclude": ["docker"], "constraints": ["..."]}}.
    # By default packs auto-attach to an agent via their `applies_to`.
    "contracts": {},
}


def load(root: Path | None = None) -> dict[str, Any]:
    root = root or util.config_root()
    data = util.read_json(root / "config.json", default={}) or {}
    cfg = {**DEFAULTS, **data}
    if not cfg.get("project_name"):
        cfg["project_name"] = util.project_root(root).name
    return cfg
