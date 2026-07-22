# Context — Visual & Responsive QA

## Why this pack exists

Most UI bugs are **invisible to unit tests and typecheck**: a button that slides
off-screen at 360px, a navbar that wraps on a tablet, text that overflows its
card, a hero image that shifts the layout as it loads, gray-on-white text that
fails contrast. They only surface when a human opens the browser and looks — the
slowest, most-skipped step in the loop.

This pack gives the AI that step **as an automated capability**: drive the real
running app in a real browser, look at it across the devices real users have, and
measure what "looks right" actually means (no overflow, adequate contrast, stable
layout, fast paint). The AI sees the result, fixes it, and proves the fix — before
you ever open the browser.

## Doctrine

- **Test the running app, not a mock.** Start the dev server (verify the port
  first — `nxai port`), then drive the live URL. Screenshots of a mocked DOM lie.
- **Mobile-first, matrix-always.** Every key route is checked across the full
  device matrix (see `device-matrix.md`), smallest width first. "Works on my
  1920px monitor" is not a pass.
- **Detect, don't guess.** Overflow is `scrollWidth > clientWidth`, not a hunch.
  Contrast is a computed ratio. CLS is a measured number. Lighthouse is a score.
- **QA reports; the developer fixes.** `visual-qa` owns the *evidence and the
  gate*; the source fix belongs to the owning developer (`responsive`, `frontend`
  or `mobile`). The loop hands the fix over and re-verifies — it does not fork
  ownership of product code.
- **Baselines are intentional.** A pixel diff that changed because the design
  changed is re-approved on purpose; a diff nobody intended is a regression.
- **Green in CI or it didn't happen.** The same thresholds run in CI so a
  regression blocks the merge, not just the local run.

## Where it sits in the pipeline

The `responsive` developer runs alongside `frontend`/`mobile` (implementation);
`visual-qa` runs after `qa` and before `reviewer` — the last gate that looks at
the product with real eyes before it ships.

## Stack assumptions

Browser automation is **Playwright** (Chromium/Firefox/WebKit + device
emulation). Perf/quality is **Lighthouse CI**. Visual regression is **BackstopJS**
(pixel diff) with **Storybook** for per-component states. The default frontend is
React/Next.js + Tailwind, but the loop is framework-agnostic — it drives a URL.
