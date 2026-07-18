# Patterns — UI Reverse Engineering

## The pipeline (canonical)
```
1. Gate      confirm ownership/authorization; record provenance (policies §0/§6)
2. Capture   Playwright: HTML · CSS · screenshots desktop+mobile · assets · fonts
             · SVG/icons · links · key interactions (capture-playbook.md)
3. Analyze   read screenshots + DOM; identify layout regions and repeated UI
4. System    distill design tokens + component inventory BEFORE code
5. Rebuild   React + Vite + Tailwind + shadcn/ui, component by component
6. Improve   fix a11y, responsiveness, semantics, performance as you rebuild
7. Verify    side-by-side desktop+mobile vs the captures; run the checklists
```

## Design-system extraction (step 4)
Turn raw captured styles into a **small, intentional** system:
- **Color** — cluster sampled colors into a palette (brand, surfaces, text,
  states). Name by role, not by hex. Map to Tailwind theme tokens / CSS vars.
- **Typography** — identify the font families, the type scale (sizes actually
  used), weights, line-heights. Collapse near-duplicates into a scale.
- **Spacing** — infer the spacing rhythm (4/8pt or the site's own) from margins/
  paddings. Prefer a scale over the exact captured px.
- **Radii, shadows, borders** — a handful of tokens, not every value seen.
- **Breakpoints** — from the desktop vs mobile captures.
- **Components** — inventory the repeated blocks: Header, Nav, Hero, Feature grid,
  Card, Pricing, Testimonial, Form, Footer, Button/variants, Badge, Modal.

Write the system down (a `design-system.md` + the token files) before building.

## Componentization (step 5)
- One component per UI role; props for the data that varies. No copy-pasted
  markup blocks.
- Use **shadcn/ui** primitives (Button, Card, Dialog, Input, Tabs…) as the base;
  style with Tailwind tokens.
- Keep content as data (arrays/props), not hardcoded in JSX, so it stays i18n-
  and CMS-ready.

## Fidelity vs. improvement
- Match the **layout and visual language** closely (that's the point).
- But **do not inherit defects**: fix contrast, focus, keyboard traps, missing
  alt, non-responsive tables, bloated DOM. Record each deviation as a decision.

## Verify (step 7)
- Screenshot the rebuild at the **same viewports** as the capture and diff by eye
  (or pixel-diff for regressions). Check both desktop and mobile.
- Confirm no unlicensed asset shipped and provenance is recorded.
