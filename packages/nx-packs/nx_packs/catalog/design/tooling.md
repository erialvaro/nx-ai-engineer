# Tooling — use it, don't hand-roll

## `ui-ux-pro-max` — design intelligence
UI/UX guidance: styles, color palettes, font pairings, chart types and per-stack
implementation (React/Next/Vue/Svelte/Tailwind/shadcn). **Use it to plan** a screen
and to **review/fix** existing UI (accessibility, layout, typography, spacing).
Reach for it *before* inventing a style from scratch.

## The 21st.dev family (catalog · AI · registry · themes)
- **`21st-cli-use`** — search & install existing React/shadcn components, themes and
  templates from the 21st.dev catalog; print a component's code. **Search the
  catalog before hand-writing UI** (auto-relevant when the project has
  `components.json`). Reuse beats rebuild.
- **`21st-ai`** — sketch/generate new UI from a prompt, preview variants, edit a
  variant in natural language, and pull the final code in. Good for exploring a
  section fast — then harden it against this pack's policies.
- **`21st-registry`** — publish your own components/themes/templates to the team
  library so the system compounds instead of fragmenting.
- **`21st-design-sync`** — publish the project's design tokens (shadcn/Tailwind CSS
  variables) as a shareable theme.

## `dataviz` — read **before** any chart
Any chart, graph, dashboard, KPI tile or sparkline: read the `dataviz` standard
first (form heuristic, accessible color formula, mark specs, interaction rules) so
visualizations read as one system in light **and** dark.

## `framer-motion` — motion
```bash
npm i framer-motion
```
See [motion.md](motion.md) for the duration/easing scale and the reduced-motion rule.

## Default stack
**shadcn/ui + Tailwind** on top of CSS-variable tokens — the same stack the
`nxai new` cloud-agnostic foundation (Next.js) ships with. Keep `components.json`,
`tailwind.config.*` and `globals.css` in sync: they are all views of the **same
tokens**.

## Workflow
1. **Plan** with `ui-ux-pro-max` (style, palette, type, layout).
2. **Reuse**: search `21st-cli-use` for an existing component/theme.
3. **Generate** only what's missing (`21st-ai`), then harden it (a11y, tokens, states).
4. **Charts** → `dataviz`. **Motion** → framer-motion.
5. **Publish** reusable results (`21st-registry`, `21st-design-sync`).
6. **Review** against `checklists.md` before handing off to `frontend`.
