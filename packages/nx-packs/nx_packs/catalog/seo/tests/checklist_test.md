# SEO test checklist (evidence required)

These are the **mandatory validations** — automate where possible in CI.

## Structured data
- [ ] Each templated page type passes the **Rich Results Test** / schema validator
- [ ] JSON-LD matches visible content (no hidden/absent markup)

## Crawl & index
- [ ] `robots.txt` passes a validator; does not block CSS/JS; `Sitemap:` present
- [ ] XML sitemap validates; contains only indexable, canonical URLs
- [ ] Sample pages: exactly one self-referential canonical; no stray `noindex`
- [ ] Rendered-HTML check: primary content visible without executing JS

## Performance
- [ ] Field Core Web Vitals within budget on key templates (LCP<2.5s, INP<200ms, CLS<0.1)
- [ ] TTFB < 800ms; LCP image optimized + prioritized; images have dimensions

## Internationalization (if applicable)
- [ ] `hreflang` reciprocal + `x-default`; each locale indexable

## AI discoverability
- [ ] `llms.txt` reachable and current
- [ ] AI-crawler policy present and matches the documented decision

Ship only when every applicable box has **evidence**, not assumption.
