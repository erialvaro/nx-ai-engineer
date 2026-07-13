# SEO context (injected brief)

You are optimizing a web app/site for **search + AI discoverability**. Treat SEO
as an engineering property of the delivered HTML, not an afterthought.

**Always ensure, per indexable page:**
- It is **crawlable** (not blocked in `robots.txt`; CSS/JS reachable) and
  **indexable** (correct `meta robots`; exactly one self-referential `canonical`).
- The **primary content is in the server-rendered HTML** (SSR/SSG/ISR) — do not
  rely on client-only rendering for content that must rank or be cited by AI.
- **Unique `<title>`** (~50–60 chars) and **`meta description`** (~150–160), a
  single `H1`, semantic heading order, descriptive `alt`, and intentional
  internal links.
- **Valid schema.org JSON-LD** matching the visible content (Organization +
  WebSite site-wide; BreadcrumbList; Article/Product/FAQ per template).
- **Core Web Vitals** budget: LCP < 2.5s, INP < 200ms, CLS < 0.1.
- **Social**: Open Graph + Twitter card tags.
- **AI**: contribute to `llms.txt`; write **answer-first**, well-structured,
  factual content; keep entities/names consistent (`sameAs`); honor the project's
  **AI-crawler policy** (GPTBot/ClaudeBot/PerplexityBot/Google-Extended).

**Site-wide invariants:** clean lowercase hyphenated URLs; HTTPS; correct
301/404/410; an XML sitemap referenced from `robots.txt`; reciprocal `hreflang`
(+`x-default`) if multi-locale.

If a task would create duplicate content, a conflicting canonical, a `noindex` on
a page meant to rank, JS-only critical content, or a CWV regression — **stop and
resolve it first** (see `anti-patterns.md`).
