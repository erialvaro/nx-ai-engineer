# Design anti-patterns (never do)

## System rot
- **Magic values** in components (`#3b82f6`, `13px`, `margin-top: 27px`) instead of
  tokens. This is how a design system dies.
- A new near-duplicate component instead of a variant of an existing one.
- "Dark mode" as a **naive inversion** — unreadable contrast, blown-out saturation,
  shadows that do nothing.
- Tokens that exist but nobody uses (a design system nobody consumes is decoration).

## Accessibility failures (blocking)
- `outline: none` with **no visible focus replacement**.
- **Contrast failures** — especially `muted-foreground` on `background`, placeholder
  text, disabled states carrying meaning, and chart marks.
- **Placeholder as label**; error shown only as a red border.
- Meaning conveyed **by color alone**; icon-only buttons with no accessible name.
- Custom `div` "buttons" that aren't keyboard reachable; modals that don't trap and
  restore focus; keyboard traps; missing skip link.
- Ignoring **`prefers-reduced-motion`**.
- Touch targets below 24px; hover-only affordances on touch devices.

## Layout & type
- Crowding (no whitespace); inconsistent spacing (values off the scale).
- Body text below 16px; line length far beyond 75ch; centered long-form body text.
- Faking hierarchy with styled `div`s instead of semantic headings.
- Too many fonts/weights/sizes; misalignment presented as "style".

## Motion
- Gratuitous animation that explains nothing; long durations (> 400ms) on common
  interactions; infinite loops near content.
- Animating **`width/height/top/left`** (layout thrash) instead of transform/opacity.
- Motion that **blocks** interaction or causes **layout shift** (CLS).

## Performance (design breaking CWV)
- Images/embeds **without dimensions** → CLS. Huge hero media → bad LCP.
- Heavy webfonts, many weights, no `font-display: swap`.
- Decorative libraries loaded for one flourish.

## Process
- Handing off a picture instead of a **spec** (tokens, states, behavior).
- Designing only the happy path — no loading/empty/error states.
- Inventing UI without checking the catalog (`21st-cli-use`) or the existing system.
