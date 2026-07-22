# Checklists — Visual & Responsive QA

## Before the run
- [ ] Dev/preview server is up; the port was verified free (`nxai port`) and the
      base URL is reachable
- [ ] Key routes to test are listed (home, auth, the main flow, pricing, dashboard…)
- [ ] Playwright installed (`npx playwright install`) with the device matrix configured

## Responsive (per route, per viewport)
- [ ] No horizontal overflow (`scrollWidth <= clientWidth`)
- [ ] Navbar/header intact — not wrapped, not clipped, menu reachable
- [ ] Buttons/CTAs fully visible and tappable; nothing off-screen
- [ ] Text does not overflow its container or truncate meaning
- [ ] Images/media sized; no layout shift as they load
- [ ] Touch targets >= 44px on touch viewports; safe areas respected on notched devices

## Accessibility (light AND dark)
- [ ] Contrast >= 4.5:1 (body) / 3:1 (large + UI) in both themes
- [ ] Visible focus on every interactive element; keyboard reaches everything
- [ ] Roles/labels/alt present; forms labelled
- [ ] `prefers-reduced-motion` honored

## Performance / Vitals
- [ ] Lighthouse Performance / Accessibility / Best-Practices / SEO all >= 95
- [ ] CLS < 0.1; LCP in the "good" band; no unsized media

## Visual regression
- [ ] BackstopJS run against approved baselines
- [ ] Diffs triaged: intended changes re-approved, unintended ones filed as regressions
- [ ] Storybook stories cover the key component states (loading/empty/error/dark)

## Loop close-out
- [ ] Each defect has a before screenshot, a fix (by the owning developer) and an after screenshot
- [ ] The full matrix re-run is green
- [ ] Thresholds pass in CI (Playwright + Lighthouse CI), not just locally
- [ ] Before/after report generated (see `templates/visual-qa-report.md`)
