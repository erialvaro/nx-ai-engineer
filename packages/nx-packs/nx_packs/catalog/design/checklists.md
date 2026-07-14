# Design checklist

## System / tokens
- [ ] Tokens defined: color, type scale, spacing, radius, shadow, z-index, motion
- [ ] Tokens are the **single source of truth** — no magic values in components
- [ ] **Light and dark** both defined (dark is designed, not just inverted)
- [ ] Reused existing tokens/components (checked the 21st.dev catalog) — no duplicates

## Typography
- [ ] A real type scale; font pairing justified
- [ ] Measure 45–75ch; line-height set; hierarchy obvious at a glance

## Color & contrast
- [ ] Palette has roles (bg / surface / fg / muted / primary / destructive)
- [ ] **Contrast verified**: ≥ 4.5:1 text, ≥ 3:1 large/UI — in **both** themes
- [ ] Meaning never conveyed by color alone

## Layout & responsive
- [ ] One spacing scale; consistent grid; deliberate whitespace
- [ ] Mobile-first; validated at the smallest breakpoint

## Accessibility (gate)
- [ ] Keyboard reachable; **visible focus ring** on every interactive element
- [ ] Semantic HTML; real labels; ARIA only where needed
- [ ] Target size ≥ 24×24px
- [ ] `prefers-reduced-motion` honored

## States (all of them)
- [ ] default / hover / focus / active / disabled
- [ ] **loading (skeleton)** / **empty** / **error** / success

## Motion
- [ ] Duration + easing scale defined; framer-motion used
- [ ] Purposeful (explains a change); never blocking; reduced-motion-safe

## Performance (with the `seo` pack)
- [ ] Media/embeds have explicit dimensions → **no CLS**
- [ ] LCP element is light and prioritized; `font-display: swap`

## Handoff
- [ ] Spec is implementable by the `frontend` agent without asking questions
- [ ] Data viz (if any) follows the `dataviz` standard
