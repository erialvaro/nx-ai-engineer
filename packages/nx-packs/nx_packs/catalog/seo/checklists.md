# SEO checklist

## Per page / route (before merge)
- [ ] Indexable: correct `meta robots`; exactly one self-referential canonical
- [ ] Not accidentally `noindex` (meta or `X-Robots-Tag`)
- [ ] Unique `<title>` (~50–60) and `meta description` (~150–160)
- [ ] Exactly one `H1`; semantic heading order; descriptive `alt`
- [ ] Primary content present in **server-rendered HTML** (view source, not devtools)
- [ ] Valid JSON-LD matching visible content (Rich Results test passes)
- [ ] Open Graph + Twitter card tags present and correct
- [ ] Internal links use descriptive anchors; no orphan page
- [ ] Core Web Vitals within budget (LCP/INP/CLS) on mobile
- [ ] Correct status code (200/301/404/410); no redirect chain; HTTPS

## Site-wide (before launch)
- [ ] `robots.txt` valid; CSS/JS not blocked; `Sitemap:` referenced
- [ ] XML sitemap(s) valid, `lastmod` accurate, only indexable URLs, submitted to
      Search Console
- [ ] Clean URL scheme (lowercase, hyphens, stable, hierarchical)
- [ ] Canonicalization strategy for params/duplicates in place
- [ ] `hreflang` reciprocal + `x-default` (if multi-locale)
- [ ] 404 page returns 404 (no soft-404); important 301s mapped
- [ ] `og:image`/favicon/`site.webmanifest` present
- [ ] Analytics + Search Console + (optional) Bing Webmaster verified

## AI / LLM discoverability
- [ ] `llms.txt` present, curated, and current
- [ ] Content is answer-first, factual, well-structured (lists/tables/FAQ)
- [ ] Entities consistent; `sameAs` links to authoritative profiles
- [ ] E-E-A-T: author/byline, sources/citations, visible dates
- [ ] Deliberate AI-crawler policy set in `robots.txt` (documented allow/deny)
- [ ] Key facts reachable in server HTML (AI crawlers often don't run JS)

## Validation tooling (evidence, not opinion)
- [ ] **PageSpeed Insights** (<https://pagespeed.web.dev/>) — Mobile **and**
      Desktop; field CWV + lab scores within budget. The SEO report is generated
      topic-by-topic from this output (see `templates/report.md`).
- [ ] Google Rich Results Test / Schema validator — pass
- [ ] `robots.txt` + sitemap validators — pass
- [ ] Mobile-friendly / rendered-HTML check — primary content visible
