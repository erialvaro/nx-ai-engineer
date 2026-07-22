# Performance & Core Web Vitals

The gate is **Lighthouse category scores >= 95** (Performance, Accessibility,
Best-Practices, SEO) on the key routes, mobile profile as the reference, plus
healthy field metrics.

## Core Web Vitals targets
- **LCP** < 2.5s (good) — largest content paints fast.
- **CLS** < 0.1 — layout is stable; nothing jumps as it loads.
- **INP** < 200ms — interactions feel responsive.

## The usual culprits (and fixes)
- **CLS** ← unsized media / injected banners / late webfonts.
  Fix: `width`+`height` or `aspect-ratio` on all media; `font-display: swap` with
  a matched fallback; reserve space for dynamic content.
- **LCP** ← unoptimized hero image / render-blocking CSS/JS.
  Fix: prioritize + preload the LCP image, use `next/image`/`expo-image`, defer
  non-critical JS, inline critical CSS.
- **Performance score** ← oversized bundles / no code-splitting / uncompressed
  assets. Fix: split routes, tree-shake, compress, lazy-load below the fold.

## Running the gate
```bash
npm install -D @lhci/cli
npx lhci autorun        # config: lighthouserc.json — assertions at 0.95
```
`lighthouserc.json` asserts each category `>= 0.95` and fails CI otherwise, so a
performance regression blocks the merge. Measure on a throttled mobile profile —
the desktop number flatters and hides real-world slowness.

## Tie-in with the loop
Lighthouse runs as **step 2** of the workflow, after the responsive matrix. A
failing audit becomes a finding handed to the owning developer, then re-verified.
