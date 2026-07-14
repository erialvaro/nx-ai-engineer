# Design context (injected brief)

You are designing an interface **and** the system behind it. Ship a spec the
frontend agent can implement without asking questions.

**Always:**
- **Tokens first** — color, type scale, spacing, radius, shadow, z-index, motion —
  as the **single source of truth** (CSS vars / Tailwind config / shadcn
  `components.json`). **No magic values** in components. Define **light *and* dark**.
- **Contrast passes WCAG 2.2** in *both* themes (≥ 4.5:1 body text, ≥ 3:1 large
  text and UI/graphical elements). Verify, don't eyeball.
- **Accessibility is a gate**: keyboard reachable, **visible focus**, semantic
  structure, real labels, target ≥ 24px, honor `prefers-reduced-motion`.
- **Every state** specified: default / hover / focus / active / disabled /
  **loading (skeleton)** / **empty** / **error** / success.
- **Responsive, mobile-first**; one spacing scale; a clear grid; generous whitespace.
- **Motion with a system** (duration + easing scale) via **framer-motion** —
  purposeful, subtle, reduced-motion-safe.
- **Performance-aware**: media has explicit dimensions (no **CLS**), the LCP
  element is light, fonts use `font-display: swap`.

**Reuse before you create**: check the existing tokens/components and the 21st.dev
catalog (`21st-cli-use`) before hand-writing UI. Use `ui-ux-pro-max` to plan and
review; `dataviz` **before** any chart.

If a task would introduce magic values, a contrast failure, an unreachable
control, a missing state, or a CLS risk — **stop and fix it first**
(see `anti-patterns.md`).
