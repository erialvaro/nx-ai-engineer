# Core Web Vitals & performance

Google uses **Core Web Vitals** (field data) as a ranking signal and a UX
standard. Budgets (75th percentile, mobile):

| Metric | Good | Meaning |
|--------|------|---------|
| **LCP** — Largest Contentful Paint | < 2.5s | main content is visible |
| **INP** — Interaction to Next Paint | < 200ms | responsiveness (replaced FID in 2024) |
| **CLS** — Cumulative Layout Shift | < 0.1 | visual stability |

## LCP (loading)
- Identify the LCP element (usually the hero image or H1 block). Make it fast:
  `priority`/eager load, preload the image/font, `fetchpriority="high"`.
- Serve AVIF/WebP, correctly sized; use a CDN; compress. `preconnect` to critical
  third-party origins.
- Minimize render-blocking CSS/JS; inline critical CSS; defer the rest.
- Prefer SSR/SSG so the first paint isn't gated on JS.

## INP (interactivity)
- Reduce main-thread work: code-split, lazy-load below-the-fold JS, avoid long
  tasks (> 50ms). Debounce heavy handlers; yield to the main thread.
- Ship less JavaScript; hydrate progressively/selectively.

## CLS (stability)
- Always set `width`/`height` (or aspect-ratio) on images/video/embeds.
- Reserve space for ads/banners/late content; avoid inserting content above
  existing content. `font-display: swap` + preloaded fonts to avoid FOIT/reflow.

## Budgets as gates
- Measure **field** CWV (RUM / CrUX / Search Console), not just lab Lighthouse.
- Set per-template budgets and treat regressions as release blockers.
- Also: TTFB (server) < 800ms; keep total transfer and request count in check.

## Measuring with PageSpeed Insights (canonical tool)
Use **PageSpeed Insights** — <https://pagespeed.web.dev/> — as the source of
truth for performance and Core Web Vitals. Run **both Mobile and Desktop**.

- It reports **field data** (CrUX, real users) for LCP/INP/CLS/FCP/TTFB **and** a
  **lab** Lighthouse run (Performance/Accessibility/Best-Practices/SEO scores +
  Opportunities + Diagnostics).
- Automate via the **PSI API**
  (`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=…&strategy=mobile`),
  which returns the same data as JSON — good for CI gates.
- The SEO report is generated **topic-by-topic from the PSI output** using the
  pack's `templates/report.md` (Core Web Vitals → Performance → Opportunities →
  Diagnostics → Accessibility → Best Practices → SEO). Report measured numbers.

Fast pages help **AI discoverability** too — answer engines favor quick,
render-stable, easily-fetched HTML.
