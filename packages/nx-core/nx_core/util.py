"""Shared utilities: path resolution, JSON/text IO, git helpers, ids, logging.

Everything here is stdlib-only so the framework runs on any machine that has
Python 3.8+ and (optionally) git. No third-party dependencies, ever.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# --- Marker that identifies the framework root inside a target project --------
CONFIG_DIRNAME = ".ai-project-assistant"


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
def config_root(start: Optional[Path] = None) -> Path:
    """Return the absolute path to the `.ai-project-assistant` directory.

    Resolution order:
      1. AIES_HOME environment variable (if set and valid).
      2. Walk up from `start` (or this file) looking for a `.ai-project-assistant` dir.
      3. Walk up looking for a directory that *is* `.ai-project-assistant`.
      4. Fall back to `<cwd>/.ai-project-assistant` — the project the user is running in.
    """
    env = os.environ.get("AIES_HOME")
    if env:
        p = Path(env).expanduser().resolve()
        if p.name == CONFIG_DIRNAME and p.is_dir():
            return p
        candidate = p / CONFIG_DIRNAME
        if candidate.is_dir():
            return candidate

    here = (start or Path(__file__)).resolve()
    for parent in [here, *here.parents]:
        if parent.name == CONFIG_DIRNAME and parent.is_dir():
            return parent
        candidate = parent / CONFIG_DIRNAME
        if candidate.is_dir():
            return candidate

    # Nothing found: default to the project the user is running in. Never point
    # into the install tree (this module may live in site-packages).
    return Path.cwd() / CONFIG_DIRNAME


def project_root(start: Optional[Path] = None) -> Path:
    """The actual project being managed = parent of `.ai-project-assistant`."""
    return config_root(start).parent


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def rel(path: Path, base: Optional[Path] = None) -> str:
    base = base or project_root()
    try:
        return str(Path(path).resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


# --------------------------------------------------------------------------- #
# IO
# --------------------------------------------------------------------------- #
def read_text(path: Path, default: str = "") -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return default


def write_text(path: Path, content: str) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return path


def read_json(path: Path, default: Any = None) -> Any:
    raw = read_text(path)
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default


def write_json(path: Path, data: Any) -> Path:
    return write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------- #
# Time / ids
# --------------------------------------------------------------------------- #
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def slugify(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].strip("-") or "task"


def short_hash(text: str, n: int = 6) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def task_id(description: str) -> str:
    """Deterministic-ish unique id: date + hash + slug."""
    return f"{today()}-{short_hash(description + now_iso())}-{slugify(description, 32)}"


# --------------------------------------------------------------------------- #
# Git
# --------------------------------------------------------------------------- #
def git(args: list[str], cwd: Optional[Path] = None,
        timeout: float = 30.0) -> tuple[int, str, str]:
    """Run a git command. Returns (returncode, stdout, stderr). Never raises.

    A timeout guards against a hung git (e.g. a credential/network prompt)."""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd or project_root()),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", "git not found on PATH"
    except subprocess.TimeoutExpired:
        return 124, "", f"git timed out after {timeout}s"


def is_git_repo(cwd: Optional[Path] = None) -> bool:
    code, out, _ = git(["rev-parse", "--is-inside-work-tree"], cwd)
    return code == 0 and out == "true"


def changed_files(base: str = "HEAD", cwd: Optional[Path] = None) -> list[str]:
    """Files changed vs `base`, plus untracked. Empty list if not a repo."""
    if not is_git_repo(cwd):
        return []
    files: set[str] = set()
    code, out, _ = git(["diff", "--name-only", base], cwd)
    if code == 0 and out:
        files.update(out.splitlines())
    code, out, _ = git(["diff", "--name-only"], cwd)  # unstaged
    if code == 0 and out:
        files.update(out.splitlines())
    code, out, _ = git(["ls-files", "--others", "--exclude-standard"], cwd)
    if code == 0 and out:
        files.update(out.splitlines())
    return sorted(f for f in files if f)


# --------------------------------------------------------------------------- #
# Console
# --------------------------------------------------------------------------- #
def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def banner(title: str) -> str:
    line = "=" * max(8, len(title) + 4)
    return f"{line}\n  {title}\n{line}"
