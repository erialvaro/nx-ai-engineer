# Visual & Responsive QA Pack

Gives the AI **eyes on a real browser**. Instead of shipping UI blind, the
`visual-qa` and `responsive` agents drive the running app with **Playwright**
across a full **device matrix**, catch what only shows up visually — horizontal
overflow, clipped buttons, broken navbars, layout shift, low contrast — measure
**Core Web Vitals**, gate **Lighthouse >= 95**, and pixel-diff against approved
baselines (**BackstopJS**). The goal is to collapse the *change → open browser →
eyeball → fix* loop into one the AI runs itself.

## The closed loop

```
1. start the app            (npm run dev / make up — verify the port first: nxai port)
2. open it in Playwright    (Chromium/Firefox/WebKit)
3. screenshot the matrix    (360x640 … 1920x1080 + named devices)
4. detect                   (overflow, clipped elements, contrast, CLS, a11y, Lighthouse)
5. hand fixes to the dev    (responsive/frontend/mobile own the source)
6. re-verify                (re-run the matrix — must be green)
7. report                   (before/after screenshots + scores)
```

## What each file covers

- **device-matrix.md** — the exact viewports and named devices every key route
  is tested against.
- **workflow.md** — the step-by-step automated loop and the Playwright/Lighthouse/
  BackstopJS commands the agent runs.
- **responsive.md** — mobile-first responsive doctrine (breakpoints, fluid type,
  no horizontal overflow, touch targets, safe areas) the `responsive` dev builds to.
- **accessibility.md** — WCAG 2.2 AA gates (contrast, focus, targets, reduce-motion).
- **performance.md** — Core Web Vitals + the Lighthouse >= 95 gate.
- **anti-patterns.md** — the layout bugs this pack exists to kill.
- **tooling.md** — Playwright, Playwright MCP, BrowserTools MCP, Lighthouse CI,
  BackstopJS, Storybook, React DevTools, Tailwind IntelliSense, ESLint, Prettier,
  Android Studio / Genymotion emulators, Chrome DevTools.
- **prompts/specialist.md** — the executor prompt.
- **templates/visual-qa-report.md** — the before/after report format.

## Agents it feeds

`visual-qa` (the QA that runs the loop and gates the merge), `responsive` (the
mobile-first web developer that applies the fixes), and the existing `frontend`
and `mobile` developers. Install with `nxai pack add visual-qa`; it then attaches
to those agents' Engineering Contracts automatically.

## Scaffold

Projects created with `nxai new` (cloud-agnostic stack) ship the loop ready to
run: `playwright.config.ts` with the device matrix, a responsive spec,
`backstop.json`, `lighthouserc.json`, a Storybook setup, npm scripts
(`test:e2e`, `test:visual`, `lhci`, `storybook`) and a `visual-qa` CI workflow.
