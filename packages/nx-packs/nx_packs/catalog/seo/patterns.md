# SEO patterns (do this)

## Rendering
- **SSR/SSG/ISR by default** for content that must rank or be cited. Static
  (SSG/ISR) for marketing/docs; SSR for personalized-but-indexable pages.
- Render metadata per route on the server (framework metadata APIs, e.g. Next.js
  `generateMetadata`), never only in the browser.

## Metadata as data
- Centralize per-route SEO in a typed config/helper (title, description, canonical,
  OG, JSON-LD) so every page is consistent and nothing is forgotten.
- Derive the canonical from the request URL minus tracking params.

## Titles & content
- Template titles as `Primary Keyword — Brand` (unique per page). Front-load the
  distinctive term.
- Answer the query in the first paragraph; then expand. Use descriptive `H2/H3`
  that mirror real questions (good for both snippets and AI answers).

## Internal linking
- Link with descriptive anchors from high-authority pages (home, hubs) to money/
  target pages. Keep important pages within ~3 clicks. Add breadcrumb navigation.

## Sitemaps & robots
- Generate the XML sitemap from the same source of truth as the router; include
  only indexable, canonical URLs with real `lastmod`. Split > 50k URLs / 50MB via
  a sitemap index. Reference it from `robots.txt`.

## Images & media
- Serve AVIF/WebP with explicit `width`/`height`; mark the LCP image `priority`
  (eager) and lazy-load the rest. Provide descriptive `alt`.

## Structured data
- Emit `Organization` + `WebSite`(+`SearchAction`) site-wide; add `BreadcrumbList`
  and the page-type schema (Article/Product/FAQ). Keep JSON-LD generated from the
  same data that renders the page, so markup and content never drift.

## Internationalization
- One URL per locale; reciprocal `hreflang` + `x-default`; localize `title`,
  `description`, and content — not just strings.

## Measurement
- Wire Search Console + field-CWV (RUM). Track index coverage, impressions, and
  CWV as release gates, not vanity metrics.
