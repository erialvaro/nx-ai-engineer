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

Fast pages help **AI discoverability** too — answer engines favor quick,
render-stable, easily-fetched HTML.
