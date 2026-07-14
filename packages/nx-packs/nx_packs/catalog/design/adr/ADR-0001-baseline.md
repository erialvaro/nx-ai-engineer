# ADR-0001 — Design baseline: tokens, accessibility, motion

- **Status:** Accepted
- **Context:** UI must be consistent as it grows, usable by everyone, fast, and
  implementable without guesswork. Ad-hoc styling and "we'll do a11y later" are how
  interfaces rot.

## Decision
Adopt this pack's standard:
- **Tokens are the single source of truth** (CSS variables → Tailwind → shadcn
  `components.json`), for **light and dark**. Components carry **no magic values**.
- **Accessibility (WCAG 2.2) is a release gate**: contrast verified in both themes,
  keyboard reachable, visible focus, semantic + labelled, `prefers-reduced-motion`.
- **Every component specifies every state** (incl. loading/empty/error).
- **Motion has a system** (duration + easing scale, framer-motion), purposeful and
  reduced-motion-safe, animating transform/opacity only.
- **Design must not regress Core Web Vitals** (no CLS from unsized media; light LCP)
  — validated with the `seo` pack.
- **Reuse before create**: `ui-ux-pro-max` to plan, `21st-cli-use` to find, `21st-ai`
  to generate the gap, `dataviz` for charts; publish reusable results back
  (`21st-registry` / `21st-design-sync`).

## Consequences
- ➕ The system compounds instead of fragmenting; the frontend agent implements from
  a spec, not a screenshot.
- ➕ Accessibility and performance are checkable, not matters of taste.
- ➖ Requires discipline (a token for every value, a state for every component) —
  enforced by the `designer` agent's checklist and this pack's
  `policies.md` / `anti-patterns.md`.
