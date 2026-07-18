# Checklists — UI Reverse Engineering

## Before capturing (gate)
- [ ] Ownership/authorization confirmed (own site, client under contract, or
      permitted inspiration) — basis recorded in the Brain
- [ ] `robots.txt` / ToS reviewed; capture scoped to a few pages; rate limited
- [ ] No auth/paywall bypass

## Capture complete
- [ ] Full-page screenshots — **desktop AND mobile** — for every target page
- [ ] Rendered HTML saved per page
- [ ] CSS extracted (cross-origin sheets skipped gracefully)
- [ ] Assets referenced: images, background-images, **fonts**, **SVG/icons**
- [ ] Main-nav links enumerated; key pages captured
- [ ] Key interactions recorded (menu open, modal, form states, hover/focus)
- [ ] `meta.json` written: source URLs, viewports, date, authorization basis

## Design system extracted (before code)
- [ ] Color palette by role (not raw hex list)
- [ ] Type scale (families, sizes, weights, line-heights)
- [ ] Spacing scale, radii, shadows, breakpoints
- [ ] Component inventory (Header, Nav, Hero, Card, Form, Footer, …)
- [ ] Written to `design-system.md` + token files

## Rebuild
- [ ] Stack = React + Vite + Tailwind + shadcn/ui (or per contract)
- [ ] Role-named, reusable components; one responsibility each
- [ ] Content is data/props, not hardcoded in JSX
- [ ] Tokens over magic numbers; no pasted style dumps
- [ ] **No literal HTML copy**; **no unlicensed third-party asset** shipped

## Improve & verify
- [ ] a11y: semantic HTML, contrast, focus-visible, keyboard nav, alt, reduced-motion
- [ ] Responsive: matches both desktop and mobile captures
- [ ] Performance: no giant DOM, no render-blocking, images sized
- [ ] Side-by-side check vs captures (desktop + mobile)
- [ ] Deviations/improvements recorded as decisions; provenance on record
