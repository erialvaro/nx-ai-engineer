# Design architecture & handoff

## Roles (who owns what)
- **`designer`** owns the **system**: tokens, theme, typography, color, spacing,
  a11y standard, motion system, component **specs** and states
  (`design/`, `tokens/`, `theme/`, `globals.css`, `tailwind.config.*`,
  `components.json`, `.storybook/`).
- **`frontend`** owns the **implementation**: components, pages, client state — built
  **from** those tokens/specs (`components/`, `*.tsx`, `*.css`).
- **`seo`** owns technical SEO/Core Web Vitals — the designer must not regress CLS/LCP.
- **`copywriter`** owns the words inside the UI.

The designer runs **before** frontend in the pipeline: design informs implementation.

## Source of truth
`globals.css` (CSS variables, `:root` + `.dark`) → Tailwind config → shadcn
`components.json`. All three are **views of the same tokens**. Changing a color in
a component is a bug; changing the token is the fix.

## Handoff artifact (what "done" means)
A **spec**, not a picture:
1. Tokens used (semantic names, not hexes).
2. Layout + responsive behavior (breakpoints, what reflows).
3. **All states**: default/hover/focus/active/disabled/loading/empty/error/success.
4. Motion: which transition, duration + easing token, reduced-motion path.
5. Accessibility: focus order, labels, roles, contrast evidence.
6. Assets: sizes/formats (with dimensions, so no CLS).

## Fit with the platform
On a `nxai new` (Next.js + Tailwind) foundation, the designer ships `globals.css`
tokens + `components.json`; the frontend agent builds with shadcn/ui; the `seo`
agent validates Core Web Vitals with PageSpeed Insights. Reusable results get
published via `21st-registry` / `21st-design-sync` so the system compounds.
