"""Worktree Manager — one isolated git worktree per agent lane.

Lets several agents work in parallel without stepping on each other's working
tree. Branches follow `<prefix>/<agent>` (default `feature/backend`, …).
Idempotent: an existing worktree/branch is reused, never recreated.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import agents as agents_mod
from . import util


def _worktrees_root() -> Path:
    # Sibling of the project so paths stay short and outside the main tree.
    return util.project_root().parent / f"{util.project_root().name}-worktrees"


def list_worktrees() -> list[str]:
    code, out, _ = util.git(["worktree", "list"])
    return out.splitlines() if code == 0 else []


def _branch_exists(branch: str) -> bool:
    code, _, _ = util.git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"])
    return code == 0


def create(agent: str, config: dict[str, Any]) -> dict[str, Any]:
    if not util.is_git_repo():
        return {"ok": False, "message": "Not a git repository — cannot create worktrees."}

    util.git(["worktree", "prune"])  # clear stale registrations first
    prefix = config.get("branch_prefix", "feature")
    branch = f"{prefix}/{agent}"
    path = _worktrees_root() / agent

    if path.exists():
        return {"ok": True, "created": False, "branch": branch, "path": str(path),
                "message": f"Worktree already exists at {path} (reused)."}

    util.ensure_dir(path.parent)
    if _branch_exists(branch):
        code, out, err = util.git(["worktree", "add", str(path), branch])
    else:
        code, out, err = util.git(["worktree", "add", "-b", branch, str(path)])

    if code != 0:
        return {"ok": False, "branch": branch, "path": str(path), "message": err or out}
    return {"ok": True, "created": True, "branch": branch, "path": str(path),
            "message": f"Created worktree {branch} at {path}"}


def create_for_plan(agent_names: list[str], config: dict[str, Any]) -> list[dict[str, Any]]:
    reg = agents_mod.registry(config)
    results = []
    for agent in agent_names:
        spec = reg.get(agent)
        if not spec or spec.read_only:  # review/architect/etc. need no lane
            continue
        results.append(create(agent, config))
    return results
