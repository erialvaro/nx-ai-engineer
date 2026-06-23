#!/usr/bin/env python
"""Stdlib-only static site generator for nx-ai-engineer.

No third-party deps (consistent with the platform). Collects the existing
markdown — overview, architecture, guides, ADRs and a per-package index — renders
each to a simple HTML page with a shared nav, and writes them to an output dir.

    python website/generate.py [OUT_DIR]   # default: website/site

The markdown subset covers what the project docs use: ATX headings, fenced code
blocks, unordered/ordered lists, blockquotes, tables, and inline code/bold/links.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# (Section, [(title, source_path)]) — the site's table of contents.
def _toc():
    fwdocs = REPO / "packages" / "nx-cli" / "nx_cli" / "_template" / "docs"
    guides = [
        ("SDK Guide", fwdocs / "SDK_GUIDE.md"),
        ("Engine Guide", fwdocs / "ENGINE_GUIDE.md"),
        ("Workflow Guide", fwdocs / "WORKFLOW_GUIDE.md"),
        ("Plugin Guide", fwdocs / "PLUGIN_GUIDE.md"),
        ("Knowledge Guide", fwdocs / "KNOWLEDGE_GUIDE.md"),
        ("Project Brain", fwdocs / "PROJECT_BRAIN.md"),
        ("Project Knowledge", fwdocs / "PROJECT_KNOWLEDGE.md"),
        ("Architecture Overview", fwdocs / "ARCHITECTURE_OVERVIEW.md"),
        ("Migration Guide", fwdocs / "MIGRATION_GUIDE.md"),
    ]
    adrs = sorted((fwdocs / "adr").glob("ADR-*.md")) if (fwdocs / "adr").is_dir() else []
    sections = [
        ("Overview", [("Home", REPO / "README.md"), ("Roadmap", REPO / "ROADMAP.md"),
                      ("Changelog", REPO / "CHANGELOG.md")]),
        ("Architecture", [("Architecture", REPO / "docs" / "ARCHITECTURE.md"),
                          ("Migration Plan", REPO / "docs" / "MIGRATION_PLAN.md")]),
        ("Guides", [(t, p) for t, p in guides if p.exists()]),
        ("ADRs", [(p.stem, p) for p in adrs]),
    ]
    return [(s, items) for s, items in sections if items]


# ---- minimal markdown -> HTML (stdlib only) -------------------------------

def _inline(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "`":
            j = text.find("`", i + 1)
            if j != -1:
                out.append("<code>" + html.escape(text[i + 1:j]) + "</code>")
                i = j + 1
                continue
        m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", text[i:])
        if m:
            out.append(f'<a href="{html.escape(m.group(2))}">{html.escape(m.group(1))}</a>')
            i += m.end()
            continue
        m = re.match(r"\*\*([^*]+)\*\*", text[i:])
        if m:
            out.append("<strong>" + html.escape(m.group(1)) + "</strong>")
            i += m.end()
            continue
        out.append(html.escape(c))
        i += 1
    return "".join(out)


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", line):
            out.append("<ul>")
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                out.append("<li>" + _inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            out.append("<ol>")
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                out.append("<li>" + _inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("</ol>")
            continue
        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(_table(rows))
            continue
        if line.startswith(">"):
            out.append("<blockquote>" + _inline(line[1:].strip()) + "</blockquote>")
            i += 1
            continue
        if line.strip() == "":
            i += 1
            continue
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#|```|\s*[-*]\s|\s*\d+\.\s|>|\|)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>" + _inline(" ".join(para)) + "</p>")
    return "\n".join(out)


def _table(rows: list[str]) -> str:
    def cells(r):
        return [c.strip() for c in r.strip().strip("|").split("|")]
    if len(rows) >= 2 and set(rows[1].replace("|", "").strip()) <= set("-: "):
        head, body = cells(rows[0]), rows[2:]
    else:
        head, body = None, rows
    out = ["<table>"]
    if head:
        out.append("<thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head) + "</tr></thead>")
    out.append("<tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells(r)) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


_CSS = """
body{max-width:54rem;margin:0 auto;padding:2rem;font:16px/1.6 system-ui,sans-serif;color:#1b1f24}
nav{border-bottom:1px solid #ddd;margin-bottom:2rem;padding-bottom:1rem}
nav b{display:block;margin-top:.6rem;color:#666;font-size:.8rem;text-transform:uppercase}
nav a{margin-right:1rem;color:#0969da;text-decoration:none}
pre{background:#f6f8fa;padding:1rem;overflow:auto;border-radius:6px}
code{background:#f0f1f2;padding:.1rem .3rem;border-radius:4px}
pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:.4rem .6rem;text-align:left}
blockquote{border-left:3px solid #ddd;margin:0;padding-left:1rem;color:#555}
"""


def _nav(toc, depth_prefix="") -> str:
    parts = ['<nav><a href="%sindex.html"><strong>nx-ai-engineer</strong></a>' % depth_prefix]
    for section, items in toc:
        parts.append(f"<b>{html.escape(section)}</b>")
        for title, path in items:
            parts.append(f'<a href="{depth_prefix}{_slug(path)}.html">{html.escape(title)}</a>')
    parts.append("</nav>")
    return "".join(parts)


def _slug(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")


def _page(title, body_html, nav_html) -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(title)} — nx-ai-engineer</title><style>{_CSS}</style></head>"
            f"<body>{nav_html}<main>{body_html}</main></body></html>")


def build(out_dir: Path | None = None) -> Path:
    out = Path(out_dir) if out_dir else REPO / "website" / "site"
    out.mkdir(parents=True, exist_ok=True)
    toc = _toc()
    nav = _nav(toc)

    # per-package API index (names + one-line summaries from each package __init__)
    pkg_rows = ["| Package | Version | Summary |", "|---|---|---|"]
    for d in sorted((REPO / "packages").glob("nx-*")):
        init = next(d.glob("*/__init__.py"), None)
        summary, ver = "", ""
        if init:
            txt = init.read_text(encoding="utf-8")
            mdoc = re.search(r'"""(.+?)(?:\n|""")', txt)
            summary = mdoc.group(1).strip() if mdoc else ""
            mv = re.search(r'__version__\s*=\s*"([^"]+)"', txt)
            ver = mv.group(1) if mv else ""
        pkg_rows.append(f"| {d.name} | {ver} | {summary} |")
    packages_md = "# Packages\n\nThe platform ships as 8 acyclic packages.\n\n" + "\n".join(pkg_rows)

    pages = 0
    for section, items in toc:
        for title, path in items:
            body = md_to_html(path.read_text(encoding="utf-8")) if path.exists() else "<p>(missing)</p>"
            (out / f"{_slug(path)}.html").write_text(_page(title, body, nav), encoding="utf-8")
            pages += 1
    # Packages page
    (out / "packages.html").write_text(_page("Packages", md_to_html(packages_md), nav), encoding="utf-8")
    # Home/index
    home_src = REPO / "README.md"
    home_body = md_to_html(home_src.read_text(encoding="utf-8")) if home_src.exists() else "<h1>nx-ai-engineer</h1>"
    (out / "index.html").write_text(_page("Home", home_body, nav), encoding="utf-8")
    pages += 2
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    out = build(Path(argv[0]) if argv else None)
    n = len(list(out.glob("*.html")))
    print(f"site generated: {out}  ({n} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
