# Design References — policies (non-negotiable)

- **Adapt, never clone.** A reference is a *starting language*, not an asset to
  copy. Re-derive tokens into the project's own system; the output must be a
  distinct brand, not a reproduction of the source site.
- **Tokens, not magic values.** The reference palette enters the codebase as
  named tokens (bg / surface / primary / accent / fg / muted) in **light AND
  dark** — never hard-coded hexes scattered in components.
- **Honor the pairing or justify the swap.** Keep the reference's display + body
  type pairing, or document why a substitute is used (licensing, locale, brand).
- **The design gates still bind.** WCAG 2.2 contrast in both themes, keyboard
  reachability + visible focus, all component states, motion system, no CLS —
  a reference never overrides the `design` pack's mandatory checks.
- **Match honestly.** If no reference genuinely fits the prompt's context, say so
  and design from first principles — do not force an unrelated reference.
- **Attribute the source.** Record which reference (and its source URL) informed
  the design in the Brain `decisions` facet, so the lineage is traceable.
