"""Project Analyzer + Audit Engine.

Discovers, at runtime, *what kind of project this is* without assuming any
technology. The result is persisted to `.ai-project-assistant/memory/architecture.json`
and reused by every later stage (planner, locks, review, agents).

The audit step layers risk/quality signals on top of the raw discovery.
Nothing here mutates the project — it is pure inspection.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from . import util

# Directories we never descend into when scanning.
_SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
    ".next", ".nuxt", "out", "target", "coverage", ".terraform", ".idea",
    ".vscode", ".ai-project-assistant", "vendor", ".cache", ".pytest_cache", ".mypy_cache",
}

# Manifest file -> (stack label, ecosystem).
_MANIFESTS = {
    "package.json": ("Node.js", "javascript"),
    "pnpm-workspace.yaml": ("pnpm workspace", "javascript"),
    "nx.json": ("Nx monorepo", "javascript"),
    "turbo.json": ("Turborepo", "javascript"),
    "lerna.json": ("Lerna monorepo", "javascript"),
    "pyproject.toml": ("Python", "python"),
    "requirements.txt": ("Python", "python"),
    "Pipfile": ("Python (pipenv)", "python"),
    "go.mod": ("Go", "go"),
    "Cargo.toml": ("Rust", "rust"),
    "pom.xml": ("Java (Maven)", "java"),
    "build.gradle": ("Java/Kotlin (Gradle)", "java"),
    "composer.json": ("PHP (Composer)", "php"),
    "Gemfile": ("Ruby", "ruby"),
    "mix.exs": ("Elixir", "elixir"),
    "pubspec.yaml": ("Dart/Flutter", "dart"),
}

# Substrings in dependency manifests -> framework label.
_FRAMEWORK_HINTS = {
    "react": "React", "vue": "Vue", "@angular/core": "Angular", "svelte": "Svelte",
    "next": "Next.js", "nuxt": "Nuxt", "vite": "Vite", "express": "Express",
    "fastify": "Fastify", "nestjs": "NestJS", "@nestjs/core": "NestJS",
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django", "starlette": "Starlette",
    "sqlalchemy": "SQLAlchemy", "prisma": "Prisma", "alembic": "Alembic",
    "spring-boot": "Spring Boot", "gin-gonic": "Gin", "actix": "Actix",
    "redis": "Redis", "psycopg": "PostgreSQL", "pg": "PostgreSQL", "mysql": "MySQL",
    "mongodb": "MongoDB", "mongoose": "MongoDB",
    "openai": "OpenAI", "anthropic": "Anthropic", "google-generativeai": "Gemini",
    "langchain": "LangChain", "llama-index": "LlamaIndex",
}

_CI_FILES = {
    ".github/workflows": "GitHub Actions",
    ".gitlab-ci.yml": "GitLab CI",
    "azure-pipelines.yml": "Azure Pipelines",
    "Jenkinsfile": "Jenkins",
    "cloudbuild.yaml": "Google Cloud Build",
    "bitbucket-pipelines.yml": "Bitbucket Pipelines",
    ".circleci": "CircleCI",
}


@dataclass
class Architecture:
    project_name: str = ""
    root: str = ""
    scanned_files: int = 0
    stacks: list[str] = field(default_factory=list)
    ecosystems: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    is_monorepo: bool = False
    workspaces: list[str] = field(default_factory=list)
    top_level_dirs: list[str] = field(default_factory=list)
    has_tests: bool = False
    test_dirs: list[str] = field(default_factory=list)
    has_docker: bool = False
    ci: list[str] = field(default_factory=list)
    has_iac: bool = False
    doc_files: list[str] = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)
    languages: dict[str, int] = field(default_factory=dict)
    generated_at: str = ""


_LANG_EXT = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
    ".rb": "Ruby", ".php": "PHP", ".cs": "C#", ".sql": "SQL", ".vue": "Vue",
    ".svelte": "Svelte", ".ex": "Elixir", ".dart": "Dart",
}


def analyze(root: Path | None = None) -> dict[str, Any]:
    """Walk the project and produce an Architecture dict."""
    root = (root or util.project_root()).resolve()
    arch = Architecture(project_name=root.name, root=str(root), generated_at=util.now_iso())

    found_manifests: list[Path] = []
    doc_files: list[str] = []
    test_dirs: set[str] = set()
    languages: dict[str, int] = {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".git")]
        cur = Path(dirpath)
        relbase = util.rel(cur, root)

        for fname in filenames:
            arch.scanned_files += 1
            fpath = cur / fname
            relpath = util.rel(fpath, root)

            if fname in _MANIFESTS:
                found_manifests.append(fpath)
            if fname.startswith("Dockerfile") or fname.startswith("docker-compose"):
                arch.has_docker = True
            if fname.endswith((".tf",)) or "terraform" in relpath or "/k8s/" in f"/{relpath}":
                arch.has_iac = True
            if fname.lower().endswith(".md"):
                doc_files.append(relpath)

            ext = fpath.suffix.lower()
            if ext in _LANG_EXT:
                languages[_LANG_EXT[ext]] = languages.get(_LANG_EXT[ext], 0) + 1
            if any(seg in {"test", "tests", "__tests__", "e2e", "spec"} for seg in relpath.split("/")):
                test_dirs.add(relbase or ".")

        # CI detection by path
        for marker, label in _CI_FILES.items():
            if (root / marker).exists() and label not in arch.ci:
                arch.ci.append(label)

    _classify_manifests(arch, found_manifests, root)

    arch.languages = dict(sorted(languages.items(), key=lambda kv: -kv[1]))
    arch.has_tests = bool(test_dirs)
    arch.test_dirs = sorted(test_dirs)[:20]
    arch.doc_files = sorted(doc_files)[:40]
    arch.top_level_dirs = sorted(
        d.name for d in root.iterdir() if d.is_dir() and d.name not in _SKIP_DIRS
    )
    arch.entrypoints = _find_entrypoints(root)
    arch.stacks = sorted(set(arch.stacks))
    arch.ecosystems = sorted(set(arch.ecosystems))
    arch.frameworks = sorted(set(arch.frameworks))
    return asdict(arch)


def _classify_manifests(arch: Architecture, manifests: list[Path], root: Path) -> None:
    workspaces: set[str] = set()
    for m in manifests:
        label, eco = _MANIFESTS[m.name]
        arch.stacks.append(label)
        arch.ecosystems.append(eco)
        if m.name in {"nx.json", "turbo.json", "lerna.json", "pnpm-workspace.yaml"}:
            arch.is_monorepo = True
        # Scan manifest body for framework hints.
        body = util.read_text(m).lower()
        for needle, fw in _FRAMEWORK_HINTS.items():
            if needle in body:
                arch.frameworks.append(fw)
        # Detect workspace globs.
        if m.name == "package.json":
            data = util.read_json(m, {}) or {}
            ws = data.get("workspaces")
            if isinstance(ws, dict):
                ws = ws.get("packages", [])
            if ws:
                arch.is_monorepo = True
                workspaces.update(ws if isinstance(ws, list) else [str(ws)])
    # Common monorepo conventions.
    for conv in ("apps", "packages", "libs", "services"):
        if (root / conv).is_dir():
            arch.is_monorepo = arch.is_monorepo or conv in ("apps", "libs", "packages")
            workspaces.add(f"{conv}/*")
    arch.workspaces = sorted(workspaces)


def _find_entrypoints(root: Path) -> list[str]:
    candidates = [
        "main.py", "app.py", "manage.py", "wsgi.py", "asgi.py",
        "src/main.ts", "src/index.ts", "src/main.js", "index.js",
        "cmd/main.go", "main.go", "src/main.rs",
    ]
    found = []
    for c in candidates:
        if (root / c).exists():
            found.append(c)
    return found


# --------------------------------------------------------------------------- #
# Audit: risk + quality signals derived from the architecture.
# --------------------------------------------------------------------------- #
def audit(arch: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or {}
    risks: list[str] = []
    strengths: list[str] = []

    if arch.get("has_tests"):
        strengths.append("Test suites present — changes can be validated automatically.")
    else:
        risks.append("No test directories detected — add tests before risky changes.")

    if arch.get("ci"):
        strengths.append(f"CI configured: {', '.join(arch['ci'])}.")
    else:
        risks.append("No CI pipeline detected — no automated gate on merges.")

    if arch.get("has_docker"):
        strengths.append("Containerized (Docker) — reproducible environments.")
    if arch.get("is_monorepo"):
        strengths.append("Monorepo layout — clear workspace boundaries to respect.")
        risks.append("Monorepo: a change can ripple across workspaces — scope carefully.")
    if not arch.get("doc_files"):
        risks.append("Sparse documentation — capture intent as you change code.")
    if len(arch.get("stacks", [])) > 3:
        risks.append("Polyglot stack — keep cross-language contracts in sync.")

    for rule in config.get("domain_rules", []):
        risks.append(f"Domain invariant to preserve: {rule}")

    return {
        "generated_at": util.now_iso(),
        "strengths": strengths,
        "risks": risks,
        "summary": _summary(arch),
    }


def _summary(arch: dict[str, Any]) -> str:
    parts = []
    if arch.get("stacks"):
        parts.append("/".join(arch["stacks"][:4]))
    if arch.get("frameworks"):
        parts.append("with " + ", ".join(arch["frameworks"][:6]))
    if arch.get("is_monorepo"):
        parts.append("(monorepo)")
    return " ".join(parts) or "Unknown stack"


def run_and_persist(root: Path | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Analyze + audit, persist both to memory, return the combined dict."""
    root = root or util.project_root()
    cfg_root = util.config_root()
    arch = analyze(root)
    aud = audit(arch, config)
    util.write_json(cfg_root / "memory" / "architecture.json", arch)
    util.write_json(cfg_root / "memory" / "audit.json", aud)
    return {"architecture": arch, "audit": aud}


def load_memory(root: Path | None = None) -> dict[str, Any]:
    cfg_root = util.config_root()
    return {
        "architecture": util.read_json(cfg_root / "memory" / "architecture.json", {}) or {},
        "audit": util.read_json(cfg_root / "memory" / "audit.json", {}) or {},
    }
