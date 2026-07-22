# Tooling — the Visual-QA stack

The agent uses these to *see*, *measure* and *gate* the UI. Install what the
project needs; the scaffold wires the core four (Playwright, Lighthouse CI,
BackstopJS, Storybook) automatically.

## Browser automation & vision

- **Playwright** *(essential)* — drives Chromium/Firefox/WebKit, emulates
  devices, navigates, screenshots, inspects elements, measures CLS/LCP, asserts
  no overflow. The backbone of the loop.
  ```bash
  npm install -D @playwright/test
  npx playwright install
  ```
- **Playwright MCP** — gives Claude Code live "eyes": open the browser, click,
  scroll, type, screenshot, compare before/after — interactively, not just via a
  scripted spec. Configure as an MCP server in Claude Code.
- **BrowserTools MCP** — inspect CSS, tweak styles, read the DOM, analyze
  performance and rendering. Especially handy with Tailwind class debugging.

## Quality & regression

- **Lighthouse CI (`@lhci/cli`)** — automates Performance / Accessibility /
  Best-Practices / SEO scoring; `lighthouserc.json` asserts `>= 0.95` and fails
  CI. `npx lhci autorun`.
- **BackstopJS** — pixel-diff visual regression against approved baselines; the
  mature open choice. Catches "button moved / navbar broke / padding changed".
  `npx backstop test` / `npx backstop approve`.
  - Alternatives: **Argos**, **Loki**, **Percy** (hosted). BackstopJS is the
    default here (open, local, mature).
- **`@axe-core/playwright`** — WCAG violations inside the Playwright run.

## Components

- **Storybook** — isolate and test components state-by-state
  (loading/empty/error/dark); pairs with BackstopJS for per-component diffs.
  `npx storybook init`.

## React / Vite / Tailwind dev aids

- **React DevTools** — component tree, props, re-render inspection.
- **Tailwind CSS IntelliSense** — class autocomplete + linting.
- **ESLint** + **Prettier** — consistency and a clean baseline for diffs.
- **Chrome DevTools** — device toolbar, the CSS/layout ground truth.

## Mobile emulation (optional)

- **Android Studio emulator** — Pixels, tablets, foldables; real Android engine.
- **Genymotion** — lighter Android emulation.
- **Playwright device mode** — covers most React/web cases with no emulator
  (iPhone SE/15/16, Pixel 9, Galaxy S24, iPad, desktop) — reach for a real
  emulator only when a native gesture or true Safari/DPR quirk is suspected.

## How it ties together

Playwright drives the **device matrix** (`device-matrix.md`) → Lighthouse scores
quality → BackstopJS guards against visual regressions → Storybook covers
component states → the loop (`workflow.md`) runs them in order and reports
before/after. The `nxai port` command verifies the dev port before the app is
brought up.
