# ADR-0001 — SEO & AI-discoverability baseline

- **Status:** Accepted
- **Context:** Web apps/sites must be discoverable and correctly ranked by both
  classic search (Google/Bing) and AI answer engines, as an engineering property
  of the delivered HTML — not a post-hoc marketing task.

## Decision
Adopt this pack's standard as the SEO baseline:
- Content that must rank or be cited is **server-rendered** (SSR/SSG/ISR) with
  per-route metadata, one self-referential canonical, and valid schema.org JSON-LD.
- Site-wide `robots.txt` (CSS/JS reachable, sitemap referenced), an XML sitemap of
  indexable URLs, clean URLs, correct status codes, and `hreflang` for i18n.
- **Core Web Vitals** budgets (LCP<2.5s, INP<200ms, CLS<0.1) are release gates.
- **AI discoverability** is first-class: `llms.txt`, answer-first structured
  content, E-E-A-T + entity clarity, and a documented AI-crawler policy.

## Consequences
- ➕ Pages are crawlable, indexable, fast, structured, and citable by AI engines.
- ➕ SEO regressions are caught by validation (Rich Results, CWV, robots/sitemap)
  wired as gates — not discovered after a ranking drop.
- ➖ Requires SSR/SSG discipline and per-route metadata plumbing; enforced via the
  `seo` agent's checklist and this pack's `policies.md` / `anti-patterns.md`.
