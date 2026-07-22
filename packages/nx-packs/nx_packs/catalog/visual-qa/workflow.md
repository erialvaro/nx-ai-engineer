# The Automated Visual-QA Loop

The exact sequence the `visual-qa` agent runs on any UI change. It turns "change →
open browser → eyeball → fix" into one loop the AI drives end to end.

## 0. Start the app on a known-free port

```bash
PORT=$(nxai port 5173 -q)        # or 3000 for Next.js — verify BEFORE binding
npm run dev -- --port "$PORT"    # or: make up
# wait until the URL responds (Playwright webServer handles this in config)
```

## 1. Drive it in a real browser (Playwright)

```bash
npm install -D @playwright/test
npx playwright install
npx playwright test               # runs the device-matrix spec
```

The spec loops the **device matrix** (see `device-matrix.md`) over each key route
and, per viewport:

- **screenshots** full-page (before),
- asserts **no horizontal overflow**:
  `expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()`,
- asserts **key elements are in-viewport** (nav, primary CTA, footer) via
  `boundingBox()` inside the viewport,
- captures **CLS/LCP** via the web-vitals PerformanceObserver.

## 2. Measure quality (Lighthouse CI)

```bash
npm install -D @lhci/cli
npx lhci autorun                  # asserts perf/a11y/best-practices/seo >= 0.95
```

## 3. Pixel-diff against baselines (BackstopJS)

```bash
npm install -D backstopjs
npx backstop test                 # diff vs approved reference
# intended change? -> npx backstop approve
```

## 4. Detect → hand off → fix

Collect every finding (overflow width, clipped element selector, contrast pair,
CLS value, failing Lighthouse audit) into the report. **The fix is applied by the
owning developer** — `responsive` for layout/breakpoints, `frontend` for
component/web, `mobile` for RN/Expo. `visual-qa` does not edit product source; it
specifies the defect precisely enough to fix in one pass.

## 5. Re-verify

Re-run steps 1–3. The loop is not done until the **full matrix is green** and the
after-screenshots prove it.

## 6. Report

Generate the before/after report (`templates/visual-qa-report.md`): per route,
per viewport, the before shot, the defect, the fix, the after shot, and the
Lighthouse/Vitals deltas.

## Giving Claude "eyes" interactively — MCP

For exploratory work (not just the scripted spec), the **Playwright MCP** and
**BrowserTools MCP** servers let the agent open the browser, click, scroll, type,
inspect the DOM/CSS and screenshot live. Configure them in Claude Code and the
agent can *look* and *compare before/after* directly. See `tooling.md`.

## Natural-language commands this enables

> Open localhost:5173 · Test iPhone 15 Pro, Pixel 9, iPad and desktop · Fix every
> horizontal overflow · Make Lighthouse >= 95 · Show me before/after.
