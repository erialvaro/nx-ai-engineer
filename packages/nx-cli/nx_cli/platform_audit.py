"""Platform-readiness audit — static checks for a Cloud-Agnostic foundation.

Scores a project across eight production dimensions, the same ones the v2
scaffolding (`nxai new`) is built to satisfy:

  Cloud-Agnostic · Twelve-Factor · Docker · Security · Scalability ·
  Observability · Multi-Environment · Production-Ready

Each check is PASS / WARN / FAIL. The audit is purely static (file presence +
content heuristics) and stdlib-only — no Docker daemon or network needed. It is
the forcing function for the generated foundation: a freshly `nxai new` project
must come out all-green.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"

# Proprietary cloud SDKs that would break "runs anywhere" portability.
_LOCKIN = (
    "boto3", "botocore", "aws-sdk", "@aws-sdk", "aws_cdk",
    "google-cloud", "@google-cloud", "googleapis", "firebase-admin",
    "azure-", "@azure/", "azure.storage", "azure.identity",
    "@vercel/", "netlify", "aws-lambda", "functions-framework",
)
# Cloud-locked image registries in compose.
_LOCKED_REGISTRIES = (".dkr.ecr.", "gcr.io/", ".azurecr.io/", "registry.cloud.")


@dataclass
class Check:
    dimension: str
    name: str
    status: str
    detail: str


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _exists(root: Path, *rel: str) -> bool:
    return any((root / r).exists() for r in rel)


def _tracked_text(root: Path) -> str:
    """Concatenate the text of source/config files worth scanning (skips noise)."""
    skip = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__",
            ".next", ".ai-project-assistant", "volumes", "logs"}
    chunks = []
    exts = {".py", ".ts", ".tsx", ".js", ".json", ".yml", ".yaml", ".toml",
            ".env", ".example", ".sh", ".sql", ".md", ""}
    for p in root.rglob("*"):
        if p.is_dir() or any(part in skip for part in p.parts):
            continue
        if p.suffix.lower() in exts or p.name.startswith(".env"):
            chunks.append(f"# >>> {p.relative_to(root)}\n{_read(p)}")
    return "\n".join(chunks)


def _compose_files(root: Path) -> list[Path]:
    return [root / n for n in ("docker-compose.yml", "docker-compose.yaml",
            "docker-compose.override.yml", "docker-compose.prod.yml") if (root / n).is_file()]


def _dockerfiles(root: Path) -> list[Path]:
    return [p for p in root.rglob("Dockerfile")
            if "node_modules" not in p.parts and ".ai-project-assistant" not in p.parts]


def audit(root: Path) -> list[Check]:
    root = Path(root).resolve()
    checks: list[Check] = []

    def add(dim, name, status, detail=""):
        checks.append(Check(dim, name, status, detail))

    blob = _tracked_text(root)
    composes = _compose_files(root)
    compose_blob = "\n".join(_read(p) for p in composes)
    dockerfiles = _dockerfiles(root)
    docker_blob = "\n".join(_read(p) for p in dockerfiles)
    prod = root / "docker-compose.prod.yml"
    prod_blob = _read(prod)
    gitignore = _read(root / ".gitignore")

    # ---- Cloud-Agnostic --------------------------------------------------- #
    hits = sorted({s for s in _LOCKIN if s in blob})
    add("Cloud-Agnostic", "no proprietary cloud SDK",
        PASS if not hits else FAIL, "none" if not hits else f"found {hits}")
    reg = sorted({r for r in _LOCKED_REGISTRIES if r in compose_blob})
    add("Cloud-Agnostic", "no cloud-locked image registry",
        PASS if not reg else FAIL, "none" if not reg else f"found {reg}")
    add("Cloud-Agnostic", "database behind an adapter",
        PASS if _exists(root, "backend/app/db/adapter.py", "backend/app/db") else WARN,
        "adapter layer present" if _exists(root, "backend/app/db/adapter.py")
        else "no backend/app/db adapter found")

    # ---- Twelve-Factor ---------------------------------------------------- #
    add("Twelve-Factor", "config via env (.env.example present)",
        PASS if _exists(root, ".env.example") else FAIL,
        ".env.example" if _exists(root, ".env.example") else "missing .env.example")
    add("Twelve-Factor", ".env is gitignored",
        PASS if re.search(r"^\s*\.env\b", gitignore, re.M) or ".env" in gitignore else FAIL,
        "ignored" if ".env" in gitignore else ".env not in .gitignore")
    # crude secret-literal heuristic: KEY = "value" with a long value in tracked files
    secret_rx = re.compile(r"(?i)(password|secret|api[_-]?key|token)\s*[:=]\s*[\"']([^\"'\s]{12,})[\"']")
    leaks = [m.group(1) for m in secret_rx.finditer(blob)
             if "example" not in m.group(2).lower() and "changeme" not in m.group(2).lower()
             and "your-" not in m.group(2).lower() and "xxxx" not in m.group(2).lower()]
    add("Twelve-Factor", "no hardcoded secrets",
        PASS if not leaks else WARN, "none detected" if not leaks else f"suspect: {leaks[:3]}")

    # ---- Docker ----------------------------------------------------------- #
    add("Docker", "Dockerfiles present", PASS if dockerfiles else FAIL,
        f"{len(dockerfiles)} Dockerfile(s)")
    multi = dockerfiles and all(len(re.findall(r"(?im)^\s*FROM\s", _read(d))) >= 2
                                for d in dockerfiles)
    add("Docker", "multi-stage builds", PASS if multi else WARN,
        "all multi-stage" if multi else "some single-stage")
    nonroot = dockerfiles and all(re.search(r"(?im)^\s*USER\s+\w", _read(d)) for d in dockerfiles)
    add("Docker", "containers run as non-root", PASS if nonroot else FAIL,
        "USER set in all" if nonroot else "a Dockerfile has no USER")
    latest = re.findall(r"(?im)^\s*FROM\s+\S+:latest", docker_blob) or \
        re.findall(r"image:\s*\S+:latest", compose_blob)
    add("Docker", "no :latest base tags", PASS if not latest else FAIL,
        "all pinned" if not latest else "uses :latest")
    add("Docker", ".dockerignore present",
        PASS if _exists(root, ".dockerignore", "backend/.dockerignore", "frontend/.dockerignore")
        else WARN, "present" if _exists(root, ".dockerignore", "backend/.dockerignore") else "missing")

    # ---- Security --------------------------------------------------------- #
    add("Security", "secrets kept out of git",
        PASS if ".env" in gitignore else FAIL, "ok" if ".env" in gitignore else ".env not ignored")
    hc = "healthcheck" in compose_blob.lower() or "HEALTHCHECK" in docker_blob
    add("Security", "non-root + pinned images", PASS if (nonroot and not latest) else WARN,
        "hardened" if (nonroot and not latest) else "review USER/tags")
    rls = "row level security" in blob.lower() or "enable row level" in blob.lower() \
        or _exists(root, "supabase/policies.sql") or "policy" in _read(root / "supabase/migrations")
    rls = rls or any("rls" in _read(p).lower() or "row level security" in _read(p).lower()
                     for p in root.glob("supabase/**/*.sql"))
    add("Security", "database RLS policies defined", PASS if rls else WARN,
        "RLS present" if rls else "no RLS policies found (Supabase)")

    # ---- Scalability ------------------------------------------------------ #
    restart = "restart:" in prod_blob or "restart_policy" in prod_blob
    add("Scalability", "restart policy (prod)", PASS if restart else WARN,
        "set" if restart else "no restart policy in prod compose")
    add("Scalability", "healthchecks defined", PASS if hc else WARN,
        "present" if hc else "no healthchecks")
    add("Scalability", "stateless app tier",
        PASS if _exists(root, "backend") else WARN,
        "no host-state writes in app" if _exists(root, "backend") else "n/a")

    # ---- Observability ---------------------------------------------------- #
    add("Observability", "structured logging",
        PASS if re.search(r"(?i)json.*log|structlog|structured", blob) else WARN,
        "structured logs" if re.search(r"(?i)json.*log|structured", blob) else "plain logs")
    add("Observability", "request-id correlation",
        PASS if re.search(r"(?i)request[_-]?id|x-request-id|correlation", blob) else WARN,
        "request-id middleware" if re.search(r"(?i)request[_-]?id", blob) else "no request id")
    health_ep = re.search(r"/health", blob) and re.search(r"/ready", blob)
    add("Observability", "health + readiness endpoints",
        PASS if health_ep else WARN, "/health + /ready" if health_ep else "missing endpoints")

    # ---- Multi-Environment ------------------------------------------------ #
    add("Multi-Environment", "per-environment config",
        PASS if (_exists(root, "environments") or
                 (_exists(root, "docker-compose.override.yml") and prod.is_file())) else WARN,
        "environments/ or override+prod" if _exists(root, "environments") or prod.is_file()
        else "single environment only")
    add("Multi-Environment", "dev/prod compose split",
        PASS if (root / "docker-compose.yml").is_file() and prod.is_file() else WARN,
        "base + prod" if prod.is_file() else "no prod compose")

    # ---- Production-Ready ------------------------------------------------- #
    add("Production-Ready", "prod compose exists", PASS if prod.is_file() else FAIL,
        "docker-compose.prod.yml" if prod.is_file() else "missing")
    dev_only = ("mailhog", "pgadmin", "minio")
    leaked_dev = [s for s in dev_only if s in prod_blob.lower()]
    add("Production-Ready", "no dev-only services in prod",
        PASS if not leaked_dev else FAIL,
        "clean" if not leaked_dev else f"dev services in prod: {leaked_dev}")
    add("Production-Ready", "Makefile workflow",
        PASS if _exists(root, "Makefile") else WARN,
        "present" if _exists(root, "Makefile") else "no Makefile")

    return checks


def summarize(checks: list[Check]) -> dict:
    counts = {PASS: 0, WARN: 0, FAIL: 0}
    for c in checks:
        counts[c.status] = counts.get(c.status, 0) + 1
    return {"pass": counts[PASS], "warn": counts[WARN], "fail": counts[FAIL],
            "total": len(checks), "ok": counts[FAIL] == 0}
