# Design quality gate (evidence required)

Blocking — a design does not ship with a failure here.

## Accessibility (WCAG 2.2)
- [ ] Contrast ≥ **4.5:1** body / **3:1** large + UI — verified in **light**
- [ ] Same, verified in **dark**
- [ ] Every interactive element keyboard reachable, in logical order
- [ ] **Visible focus ring** everywhere (no bare `outline: none`)
- [ ] Semantic HTML; real labels; accessible names on icon-only controls
- [ ] Target size ≥ 24×24px
- [ ] `prefers-reduced-motion` honored (verified)
- [ ] axe / Lighthouse a11y audit passes

## System
- [ ] No magic values — components consume **tokens** only
- [ ] Light **and** dark token sets defined and validated
- [ ] No duplicate component (catalog + existing system checked)

## Completeness
- [ ] loading/skeleton, empty, error states exist (not just the happy path)

## Motion
- [ ] Uses the duration/easing scale; transform/opacity only; never blocking

## Performance (with the `seo` pack)
- [ ] Media/embeds have explicit dimensions → **CLS < 0.1**
- [ ] LCP element light/prioritized; `font-display: swap`
- [ ] PageSpeed Insights shows no CWV regression

## Data viz (if applicable)
- [ ] Follows the `dataviz` standard (accessible palette, consistent marks)

Ship only when every applicable box has **evidence**, not assumption.
