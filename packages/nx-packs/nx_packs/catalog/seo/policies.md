# SEO policies (non-negotiable)

## Crawlability
- `robots.txt` MUST NOT block CSS/JS or important content paths. Use it to keep
  bots out of infinite/duplicate spaces (search results, faceted params), not to
  hide indexable pages.
- Reference the XML sitemap from `robots.txt` (`Sitemap:` line).
- Avoid crawl traps: parameterized/faceted URLs must be canonicalized or blocked.

## Indexability
- Every page has **exactly one** self-referential `<link rel="canonical">`; never
  conflicting or cross-domain canonicals unless intentional.
- Pages meant to rank MUST NOT carry `noindex` (meta or `X-Robots-Tag`).
- Non-canonical duplicates (print, tracking params, session URLs) canonicalize to
  the primary URL.
- Return correct status codes: `200` live, `301` permanent moves, `404`/`410`
  gone. No **soft-404** (200 with "not found" content).

## Rendering
- The **primary content and metadata must exist in the server HTML** (SSR/SSG/ISR).
  Client-only rendering is allowed only for non-critical, non-indexed UI.
- `title`, `meta description`, canonical, Open Graph and JSON-LD are rendered
  server-side, per route.

## On-page
- Unique, descriptive `<title>` (~50–60 chars) and `meta description` (~150–160)
  per page. Exactly one `H1`; logical `H2/H3`.
- Semantic HTML5 (`<main>`, `<nav>`, `<article>`, `<header>`); descriptive `alt`
  on meaningful images; intentional, descriptive internal-link anchor text.
- Open Graph (`og:title/description/image/url/type`) + Twitter card on every page.

## Structured data
- Emit valid schema.org **JSON-LD** that **matches visible content** (no markup
  for hidden/absent content). Site-wide `Organization` + `WebSite`; `BreadcrumbList`
  on deep pages; the right type per template (Article, Product+Offer, FAQPage,
  LocalBusiness, etc.). Must pass Rich Results.

## Performance (Core Web Vitals)
- Budgets on key templates: **LCP < 2.5s, INP < 200ms, CLS < 0.1** (field data).
- Images sized/optimized (AVIF/WebP, width/height set, `loading="lazy"` below the
  fold, priority for LCP image). Preconnect/preload critical origins/assets.
  `font-display: swap`. No layout shift from late media/ads/fonts.

## Internationalization
- Multi-locale sites use reciprocal `hreflang` with `x-default`; each locale has a
  stable URL; do not `noindex` alternate locales.

## AI / LLM discoverability
- Ship `llms.txt` (a curated map of key content) and keep it current.
- Content is **answer-first**, factual, well-structured (lists/tables/headings),
  with clear entities and consistent naming (`sameAs`), and E-E-A-T signals
  (author, sources, dates).
- Set a **deliberate AI-crawler policy** in `robots.txt` (GPTBot, ClaudeBot,
  PerplexityBot, Google-Extended, CCBot) — allow or deny on purpose, documented.

## Governance
- Nothing ships that violates this file or `anti-patterns.md`. Measurable claims
  (CWV, Rich Results) are **validated**, not assumed (see `checklists.md`).
