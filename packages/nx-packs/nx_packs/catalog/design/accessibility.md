# Accessibility (WCAG 2.2) — a gate, not a wish

If it isn't accessible, it isn't done. These are **blocking** requirements.

## Perceivable
- **Contrast**: ≥ 4.5:1 body, ≥ 3:1 large text and **UI/graphical elements**
  (borders, icons, focus ring, chart marks) — verified in **light and dark**.
- **Never color alone** to convey state/meaning — pair with icon/label/text.
- Text resizes to 200% without breaking layout; no text baked into images.
- Meaningful `alt` on images; decorative images `alt=""`.

## Operable
- **Everything keyboard reachable**, in a logical tab order.
- **Visible focus ring** on every interactive element — never `outline: none`
  without an equivalent (use the `--ring` token).
- Target size ≥ **24×24px** (WCAG 2.2); prefer 44px for primary/touch.
- No keyboard traps; skip-to-content link; Esc closes overlays; focus is **trapped
  inside a modal** and **restored** on close.
- Honor **`prefers-reduced-motion`** — provide a no/reduced-motion path.

## Understandable
- Real `<label>`s (a placeholder is **not** a label). Errors are announced,
  specific, and next to the field — not just a red border.
- Consistent navigation and naming; predictable behavior.

## Robust
- **Semantic HTML first** (`button`, `nav`, `main`, `dialog`); ARIA only to fill
  gaps — a wrong ARIA role is worse than none.
- Name, role and value exposed for custom widgets; test with a screen reader.

## Verify (evidence, not opinion)
- Contrast checker (both themes) · keyboard-only pass · axe/Lighthouse a11y audit ·
  reduced-motion check · screen-reader smoke test on the key flow.
