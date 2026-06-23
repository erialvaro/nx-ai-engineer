"""Review Engine — consolidated, read-only analysis of the working diff.

Surfaces what a reviewer needs at a glance: which files changed, who owns them,
which have no accompanying tests, which are unusually large, which are
security/data sensitive, and where active locks overlap the diff. It never
edits code — it produces a report saved under `.ai-project/reviews/`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import agents as agents_mod
from . import locks as locks_mod
from . import util

_CRITICAL_TOKENS = ["auth", "security", "payment", "billing", "migration",
                    "secret", "token", "password", "crypto", "tenant", "delete"]
_TEST_TOKENS = ["test", "spec", "__tests__", "e2e"]
# AIES's own bookkeeping is not product code — never report on it.
_IGNORE_TOKENS = [".ai-project/", "__pycache__/", ".pyc"]


def _ignored(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(tok in p for tok in _IGNORE_TOKENS)


def _is_test(path: str) -> bool:
    return any(t in path.lower() for t in _TEST_TOKENS)


def _loc(path: str, root: Path) -> int:
    full = root / path
    if not full.exists() or not full.is_file():
        return 0
    return util.read_text(full).count("\n") + 1


def build(base: str, config: dict[str, Any]) -> dict[str, Any]:
    root = util.project_root()
    reg = agents_mod.registry(config)
    files = [f for f in util.changed_files(base, root) if not _ignored(f)]

    large_threshold = config.get("large_file_loc", 400)
    protected = config.get("protected_paths", [])

    by_agent: dict[str, list[str]] = {}
    without_tests: list[str] = []
    large: list[dict[str, Any]] = []
    critical: list[str] = []
    protected_hits: list[str] = []
    test_files = [f for f in files if _is_test(f)]
    source_files = [f for f in files if not _is_test(f)]

    import fnmatch
    for f in files:
        owner = agents_mod.route_file(f, reg)
        by_agent.setdefault(owner, []).append(f)
        loc = _loc(f, root)
        if loc > large_threshold:
            large.append({"file": f, "loc": loc})
        if any(t in f.lower() for t in _CRITICAL_TOKENS):
            critical.append(f)
        if any(fnmatch.fnmatch(f, p) for p in protected):
            protected_hits.append(f)

    # A source file "without tests" = no test file shares its stem/dir signal.
    test_stems = {Path(t).stem.replace(".test", "").replace(".spec", "").replace("_test", "")
                  for t in test_files}
    for f in source_files:
        if Path(f).stem in test_stems:
            continue
        without_tests.append(f)

    lock_overlap = locks_mod.conflicts_for(files)

    return {
        "generated_at": util.now_iso(),
        "base": base,
        "total_changed": len(files),
        "by_agent": by_agent,
        "without_tests": without_tests,
        "large_files": sorted(large, key=lambda x: -x["loc"]),
        "critical_changes": critical,
        "protected_violations": protected_hits,
        "lock_overlap": lock_overlap,
        "files": files,
    }


def render(report: dict[str, Any]) -> str:
    L: list[str] = []
    a = L.append
    a("# Consolidated Review Report")
    a(f"_Generated {report['generated_at']} — base `{report['base']}`_")
    a("")
    a(f"**Files changed:** {report['total_changed']}")
    a("")

    if report["protected_violations"]:
        a("## ⛔ Protected-path violations")
        for f in report["protected_violations"]:
            a(f"- `{f}` — this path is declared off-limits in config.")
        a("")

    a("## Ownership (by agent)")
    for agent, files in sorted(report["by_agent"].items()):
        a(f"- **{agent}** ({len(files)}): " + ", ".join(f"`{f}`" for f in files[:12])
          + (" …" if len(files) > 12 else ""))
    if not report["by_agent"]:
        a("- No changes detected.")
    a("")

    if report["critical_changes"]:
        a("## 🔒 Critical / sensitive changes")
        for f in report["critical_changes"]:
            a(f"- `{f}` — requires explicit tests + security review.")
        a("")

    if report["without_tests"]:
        a("## 🧪 Source changed without obvious tests")
        for f in report["without_tests"][:30]:
            a(f"- `{f}`")
        a("")

    if report["large_files"]:
        a("## 📈 Large files")
        for item in report["large_files"][:15]:
            a(f"- `{item['file']}` — {item['loc']} LOC")
        a("")

    if report["lock_overlap"]:
        a("## 🔁 Active lock overlap")
        for c in report["lock_overlap"]:
            a(f"- `{c.get('requested')}` locked by task `{c.get('task')}` ({c.get('owner')})")
        a("")

    a("## Suggested review focus")
    for s in _suggestions(report):
        a(f"- {s}")
    a("")
    return "\n".join(L)


def _suggestions(report: dict[str, Any]) -> list[str]:
    s = []
    if report["critical_changes"]:
        s.append("Start with the sensitive changes; confirm authz and data isolation.")
    if report["without_tests"]:
        s.append("Request tests for the untested source files before approving.")
    if report["large_files"]:
        s.append("Check large files for mixed concerns / opportunities to split.")
    if report["protected_violations"]:
        s.append("Block: protected paths were modified — revert or escalate.")
    if not s:
        s.append("Diff looks small and well-scoped; do a standard correctness pass.")
    return s


def run_and_persist(base: str, config: dict[str, Any]) -> dict[str, Any]:
    report = build(base, config)
    md = render(report)
    out = util.config_root() / "reviews" / f"review-{util.today()}-{util.short_hash(base + report['generated_at'])}.md"
    util.write_text(out, md)
    return {"report": report, "markdown": md, "path": str(out)}
