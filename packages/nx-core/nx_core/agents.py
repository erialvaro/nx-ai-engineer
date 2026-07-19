"""Agent registry — the single source of truth for *what each agent owns*.

This is data, not behaviour. The planner uses `route_globs` to decide which
agent owns a given file, and `keywords` to decide which agents a free-text
request involves. Agent markdown specs (agents/*.md) are the human/Claude
facing contracts; this keeps the machine-routable view in one place.

Globs are matched with fnmatch against POSIX-style relative paths.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Any, Optional

# Canonical pipeline order of agents — the SINGLE source of truth. Contracts/data
# agents come first, quality/delivery last. Imported by the planner, dispatcher
# and execution scheduler so the ordering can never diverge.
CANON_ORDER = [
    "architect", "database", "database-relational", "database-nosql",
    "database-reviewer", "security", "backend", "ai",
    "reverse-engineer", "designer", "frontend", "mobile", "seo", "copywriter", "devops", "qa", "reviewer",
    "delivery", "docs",
]


@dataclass
class Agent:
    name: str
    title: str
    role: str
    # Glob patterns this agent is allowed to touch. Empty => meta/read-only.
    route_globs: list[str] = field(default_factory=list)
    # Patterns this agent must never touch (defense in depth).
    forbidden_globs: list[str] = field(default_factory=list)
    # Free-text triggers used to map a request to agents.
    keywords: list[str] = field(default_factory=list)
    # Read-only agents never receive file ownership (e.g. reviewer).
    read_only: bool = False

    def owns(self, path: str) -> bool:
        if self.read_only or not self.route_globs:
            return False
        if any(fnmatch.fnmatch(path, g) for g in self.forbidden_globs):
            return False
        return any(fnmatch.fnmatch(path, g) for g in self.route_globs)


# --------------------------------------------------------------------------- #
# Built-in, technology-agnostic agents. Globs are broad on purpose: the
# project analyzer refines them per project, and config can extend/override.
# --------------------------------------------------------------------------- #
_BUILTIN: list[Agent] = [
    Agent(
        "architect", "Architect", "Owns system design, boundaries and trade-offs.",
        keywords=["architecture", "design", "refactor", "boundary", "module", "structure"],
        read_only=True,
    ),
    Agent(
        "planner", "Planner", "Decomposes goals into ordered, scoped subtasks.",
        keywords=["plan", "roadmap", "milestone"], read_only=True,
    ),
    Agent(
        "backend", "Backend", "Server-side logic, APIs, services, business rules.",
        route_globs=[
            "**/api/**", "**/server/**", "**/services/**", "**/backend/**",
            "**/controllers/**", "**/routes/**", "**/handlers/**", "**/usecases/**",
            "**/domain/**", "**/*.service.*", "apps/api/**", "libs/**/server/**",
        ],
        forbidden_globs=["**/migrations/**", "**/*.sql"],
        keywords=["api", "endpoint", "service", "backend", "business logic", "controller", "auth flow"],
    ),
    # Designer specialist. EXECUTES using the `design` Engineering Pack (design
    # system/tokens, typography, color, layout, accessibility, motion) — which
    # auto-attaches via `applies_to`, together with the `seo` pack (design decisions
    # move Core Web Vitals). Owns the design system/tokens/theme; the `frontend`
    # agent implements the components from it.
    Agent(
        "designer", "Designer (UI/UX)",
        "Design system, tokens, typography, color, layout, accessibility and motion.",
        route_globs=[
            "**/design/**", "**/design-system/**", "**/tokens/**", "**/theme/**",
            "**/*.tokens.json", "**/tailwind.config.*", "**/components.json",
            "**/globals.css", "**/.storybook/**", "**/storybook/**",
        ],
        forbidden_globs=["**/*.sql", "**/migrations/**", "**/api/**", "**/server/**"],
        keywords=["design", "designer", "ui", "ux", "ui/ux", "design system",
                  "tokens", "design token", "theme", "tema", "typography", "tipografia",
                  "font pairing", "color palette", "paleta", "contrast", "contraste",
                  "spacing", "grid", "layout", "hierarchy", "whitespace",
                  "accessibility", "acessibilidade", "wcag", "a11y", "focus",
                  "motion", "animation", "framer-motion", "micro-interaction",
                  "transition", "responsive", "dark mode", "glassmorphism",
                  "brutalism", "minimalism", "bento", "skeleton", "empty state",
                  "shadcn", "tailwind", "21st", "figma", "wireframe", "mockup",
                  "prototype", "dashboard design", "data viz"],
    ),
    Agent(
        "frontend", "Frontend", "UI components, client state, styling, UX.",
        route_globs=[
            "**/components/**", "**/pages/**", "**/views/**", "**/ui/**",
            "**/frontend/**", "**/client/**", "**/web/**", "**/*.tsx", "**/*.vue",
            "**/*.svelte", "**/*.css", "**/*.scss", "apps/web/**",
        ],
        forbidden_globs=["**/*.sql", "**/migrations/**"],
        keywords=["ui", "component", "frontend", "page", "screen", "css", "styling", "form", "client"],
    ),
    # Mobile specialist. EXECUTES using the `mobile` Engineering Pack (React Native
    # + Expo: architecture, navigation, native modules, performance, EAS build/
    # release, store submission), which auto-attaches via `applies_to`. The
    # `design-references` pack also feeds it (tokens/palette/type are platform-
    # agnostic). Owns RN/Expo-specific files (App entry, expo/eas/metro config,
    # screens, navigation, .native.* files) — never web (`frontend`) or server.
    Agent(
        "mobile", "Mobile (React Native + Expo)",
        "React Native / Expo apps: screens, navigation, native modules, builds and store release.",
        route_globs=[
            "App.tsx", "App.jsx", "App.js", "App.ts", "**/App.tsx", "**/App.jsx",
            "app.json", "app.config.*", "eas.json", "metro.config.*",
            "**/*.native.ts", "**/*.native.tsx",
            "**/screens/**", "**/navigation/**", "**/mobile/**", "apps/mobile/**",
            "**/expo/**", "**/react-native.config.*",
        ],
        forbidden_globs=["**/*.sql", "**/migrations/**", "**/api/**", "**/server/**"],
        keywords=["mobile", "mobile app", "app mobile", "aplicativo", "aplicativo mobile",
                  "react native", "react-native", "rn", "expo", "expo router", "expo-router",
                  "eas", "eas build", "eas submit", "ios", "android", "native", "nativo",
                  "apk", "aab", "ipa", "app store", "play store", "testflight",
                  "react navigation", "nativewind", "reanimated", "expo go",
                  "push notification", "notificação push", "tela do app", "app screen",
                  "mockup app", "mockup-app", "mockup do app", "cross-platform"],
    ),
    # Reverse-engineer specialist. EXECUTES using the `ui-reverse-engineering`
    # pack (Playwright capture -> design system -> rebuild in React+Vite+Tailwind+
    # shadcn), which auto-attaches via `applies_to`. Legally gated (own/authorized
    # sites only). Produces the design system + componentized rebuild; shares UI
    # paths with designer/frontend.
    Agent(
        "reverse-engineer", "Reverse Engineer",
        "Capture a live site's UI/UX (Playwright) and rebuild it as clean, componentized code -- layout & UX, never a literal copy.",
        route_globs=[
            "**/capture/**", "**/reverse-engineering/**", "**/design-system/**",
            "**/tokens/**", "**/components/**", "**/*.tsx",
        ],
        forbidden_globs=["**/*.sql", "**/migrations/**", "**/api/**", "**/server/**"],
        keywords=["reverse engineer", "reverse engineering", "engenharia reversa",
                  "clone site", "clonar site", "rebuild website", "reconstruir site",
                  "recreate", "recriar", "capture site", "capturar site", "playwright",
                  "scrape ui", "screenshot to code", "site to react", "redesign",
                  "migrate site", "migrar site", "replicate design", "replicar design"],
    ),
    # SEO specialist. EXECUTES using the `seo` Engineering Pack (technical +
    # on-page SEO, structured data, Core Web Vitals, and AI/LLM discoverability),
    # which auto-attaches via `applies_to`. Owns SEO-dedicated files (robots,
    # sitemaps, structured data, llms.txt); page meta stays shared with frontend.
    Agent(
        "seo", "SEO",
        "Technical & on-page SEO, indexability, structured data, and AI/LLM discoverability.",
        route_globs=[
            "**/robots.txt", "**/robots.ts", "**/sitemap*.xml", "**/sitemap*.ts",
            "**/llms.txt", "**/llms-full.txt", "**/*.jsonld", "**/structured-data/**",
            "**/seo/**", "**/*sitemap*", "**/site.webmanifest", "**/manifest.webmanifest",
            "**/humans.txt",
        ],
        forbidden_globs=["**/*.sql", "**/migrations/**", "**/api/**", "**/server/**"],
        keywords=["seo", "search engine optimization", "indexing", "indexation",
                  "sitemap", "robots.txt", "canonical", "meta description", "meta tags",
                  "structured data", "schema.org", "json-ld", "rich results", "hreflang",
                  "open graph", "core web vitals", "lcp", "inp", "cls", "lighthouse",
                  "crawl", "googlebot", "serp", "llms.txt", "ai search", "e-e-a-t",
                  "generative engine optimization", "geo", "ai overview", "discoverability"],
    ),
    # Copywriter specialist. EXECUTES using the `copywriter` Engineering Pack
    # (human-sounding writing, tech/innovation fluency, SEO-optimized copy) — which
    # auto-attaches via `applies_to`, together with the `seo` pack. Owns marketing/
    # content copy (blog, landing, articles); technical docs stay with `docs`.
    Agent(
        "copywriter", "Copywriter",
        "Professional, human-sounding copy for tech & innovation — SEO-optimized.",
        route_globs=[
            "**/content/**", "**/copy/**", "**/copywriting/**", "**/blog/**",
            "**/posts/**", "**/articles/**", "**/marketing/**", "**/landing/**",
            "**/cms/**", "**/*.mdx",
        ],
        forbidden_globs=["**/*.sql", "**/migrations/**", "**/api/**",
                         "**/server/**", "**/*.tsx"],
        keywords=["copy", "copywriter", "copywriting", "redator", "redação",
                  "conteúdo", "content", "blog", "artigo", "article", "post",
                  "landing page", "headline", "cta", "call to action", "storytelling",
                  "tom de voz", "tone of voice", "persuasão", "persuasion", "marketing",
                  "newsletter", "product copy", "tagline", "hero copy"],
    ),
    Agent(
        "database", "Database", "Schema, migrations, queries, data integrity.",
        route_globs=[
            "**/migrations/**", "**/*.sql", "**/models/**", "**/entities/**",
            "**/schema/**", "**/*.prisma", "**/alembic/**", "**/repositories/**",
        ],
        keywords=["database", "schema", "migration", "table", "query", "index", "model", "entity"],
    ),
    # Specialist database agents. They EXECUTE using the Database Engineering Packs
    # (postgres/mongodb/…), which auto-attach via `applies_to`. The generic
    # `database` agent remains the default file owner (it is earlier in CANON_ORDER);
    # these specialists are selected by the dispatcher/contract for focused work.
    Agent(
        "database-relational", "Relational Database",
        "Relational modeling & migrations using the relational Engineering Packs.",
        route_globs=[
            "**/migrations/**", "**/*.sql", "**/models/**", "**/entities/**",
            "**/schema/**", "**/*.prisma", "**/alembic/**", "**/repositories/**",
        ],
        keywords=["relational", "postgres", "postgresql", "mysql", "sql server", "oracle",
                  "sqlite", "normalization", "foreign key", "index", "explain", "migration"],
    ),
    Agent(
        "database-nosql", "NoSQL Database",
        "Document/key-value/graph modeling using the NoSQL Engineering Packs.",
        route_globs=[
            "**/models/**", "**/schemas/**", "**/*.mongo.*", "**/repositories/**",
        ],
        keywords=["nosql", "mongo", "mongodb", "document", "embedding", "referencing",
                  "redis", "cassandra", "elasticsearch", "neo4j", "graph", "shard"],
    ),
    Agent(
        "database-reviewer", "Database Reviewer",
        "Reviews data models/migrations; never implements — asks and blocks.",
        keywords=["database review", "schema review", "migration review", "model review",
                  "anti-pattern", "redundancy", "duplicate table"],
        read_only=True,
    ),
    Agent(
        "ai", "AI", "Prompts, RAG, embeddings, model selection, agent tools.",
        route_globs=[
            "**/prompts/**", "**/rag/**", "**/embeddings/**", "**/llm/**",
            "**/agents/**", "**/ai/**", "**/*.prompt.*", "**/tools/ai/**",
        ],
        forbidden_globs=["**/*.sql", "**/migrations/**", "**/*.tsx"],
        keywords=["prompt", "rag", "embedding", "llm", "model", "ai", "agent", "vector", "retrieval"],
    ),
    Agent(
        "security", "Security", "Authn/authz, secrets, input validation, crypto.",
        route_globs=[
            "**/auth/**", "**/security/**", "**/*auth*.*", "**/middleware/**",
            "**/guards/**", "**/permissions/**",
        ],
        keywords=["security", "auth", "oauth", "jwt", "token", "permission", "secret", "encryption", "vulnerability"],
    ),
    Agent(
        "devops", "DevOps", "CI/CD, containers, IaC, deployment, observability.",
        route_globs=[
            "**/Dockerfile*", "**/docker-compose*.y*ml", "**/.github/workflows/**",
            "**/terraform/**", "**/*.tf", "**/k8s/**", "**/helm/**", "**/.gitlab-ci.yml",
            "**/cloudbuild.y*ml", "**/Makefile",
        ],
        keywords=["docker", "ci", "cd", "pipeline", "deploy", "terraform", "kubernetes", "infra", "observability"],
    ),
    Agent(
        "qa", "QA", "Tests, fixtures, coverage, quality gates.",
        route_globs=[
            "**/*.test.*", "**/*.spec.*", "**/tests/**", "**/test/**",
            "**/__tests__/**", "**/e2e/**", "**/cypress/**", "**/*_test.py",
        ],
        keywords=["test", "qa", "coverage", "fixture", "e2e", "unit test", "integration test"],
    ),
    Agent(
        "reviewer", "Reviewer", "Reviews diffs; never writes product code.",
        keywords=["review", "regression", "quality check"], read_only=True,
    ),
    Agent(
        "delivery", "Delivery", "Consolidates work, PR packaging, rollout/rollback.",
        keywords=["release", "deliver", "consolidate", "pull request", "merge", "rollback"],
        read_only=True,
    ),
    Agent(
        "docs", "Documentation", "Docs, READMEs, ADRs, changelogs.",
        route_globs=["**/*.md", "docs/**", "**/README*", "**/CHANGELOG*", "**/adr/**"],
        keywords=["documentation", "docs", "readme", "changelog", "adr"],
    ),
]


def registry(config: Optional[dict[str, Any]] = None) -> dict[str, Agent]:
    """Built-in agents merged with config extras, minus disabled ones."""
    config = config or {}
    reg: dict[str, Agent] = {a.name: a for a in _BUILTIN}
    for name, spec in (config.get("extra_agents") or {}).items():
        reg[name] = Agent(
            name=name,
            title=spec.get("title", name.title()),
            role=spec.get("role", ""),
            route_globs=spec.get("route_globs", []),
            forbidden_globs=spec.get("forbidden_globs", []),
            keywords=spec.get("keywords", []),
            read_only=spec.get("read_only", False),
        )
    for name in config.get("disabled_agents") or []:
        reg.pop(name, None)
    return reg


def route_file(path: str, reg: dict[str, Agent]) -> str:
    """Best agent for a path. Most-specific (longest matching glob) wins."""
    best: tuple[int, str] = (-1, "backend")
    for agent in reg.values():
        if agent.read_only:
            continue
        for g in agent.route_globs:
            if fnmatch.fnmatch(path, g) and not any(
                fnmatch.fnmatch(path, fg) for fg in agent.forbidden_globs
            ):
                score = len(g)
                if score > best[0]:
                    best = (score, agent.name)
    return best[1]
