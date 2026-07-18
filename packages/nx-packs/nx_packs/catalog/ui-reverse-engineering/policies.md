# Policies — UI Reverse Engineering (non-negotiable)

## 0. Legal & ethical gate (STOP if unmet)
- **Only reverse-engineer sites you OWN or are AUTHORIZED to rebuild** — your own
  redesign/migration, a client site under contract, or clearly-permitted
  inspiration. If ownership/authorization is unclear, **ask and stop** until
  confirmed. Record the basis in the Brain (`decisions`).
- **Respect `robots.txt`, Terms of Service and rate limits.** Do not hammer the
  origin; a handful of page loads, not a crawl. Never bypass paywalls or auth you
  were not given.
- **Never capture behind authentication** unless you were given the credentials
  for that purpose and the ToS allows it.
- **Do not reuse third-party intellectual property**: logos, brand names,
  trademarked marks, copyrighted images, proprietary fonts, and verbatim copy are
  **not** yours to ship. Replace them with placeholders/licensed equivalents, or
  flag them for the owner to supply. Capturing them as *reference* is fine;
  *shipping* them is not.

## 1. Rebuild, never copy
- Ship **refactored, componentized code** — never a literal HTML/CSS paste. The
  output must read like a senior engineer wrote it from a spec, not a scrape.
- Reproduce **layout and UX**, not the DOM. Re-derive structure into semantic,
  reusable components.

## 2. Extract a design system BEFORE writing code
- Distill **colors, typography, spacing scale, radii, shadows, breakpoints,
  motion** into tokens. Rebuild against tokens, not magic numbers pulled from the
  source CSS.

## 3. Stack & structure (default)
- **React + Vite + Tailwind + shadcn/ui** unless the contract says otherwise.
- Break into role-named components: `Header`, `Nav`, `Hero`, `Features`, `Card`,
  `Form`, `Footer`, … One responsibility per component; no god-components.

## 4. Capture desktop AND mobile
- Always capture both viewports (e.g. 1920×1080 and 390×844) and rebuild
  **responsive**. A desktop-only capture is an incomplete capture.

## 5. Improve, don't inherit flaws
- Where the source is weak, **fix it**: semantic HTML, color contrast, focus
  states, keyboard nav, alt text, reduced-motion, performance (no giant DOM, no
  render-blocking). Note each improvement.

## 6. Provenance on record
- Record source URL(s), capture date, viewport sizes, and the authorization basis
  in the Brain. A rebuild with no provenance is not done.

> Violating §0 (legal/ethical) or §1 (literal copy) means **stop and fix** — those
> are hard stops, not style notes.
