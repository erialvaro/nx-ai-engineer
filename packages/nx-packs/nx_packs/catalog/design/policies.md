# Design policies (non-negotiable)

## Tokens are law
- Color, type scale, spacing, radius, shadow, z-index and motion live as **tokens**
  (CSS variables / Tailwind theme / shadcn `components.json`) — the **single source
  of truth**. Components consume tokens; **no magic values** (`#3b82f6`, `13px`,
  `margin-top: 27px`) in component code.
- Every token set is defined for **light *and* dark**. A theme is not "dark mode"
  until it is designed, not just inverted.

## Accessibility is a gate (WCAG 2.2)
- **Contrast**: ≥ **4.5:1** for body text, ≥ **3:1** for large text and UI/graphical
  elements — verified in **both** themes.
- Every interactive element is **keyboard reachable** with a **visible focus ring**
  (never `outline: none` without a replacement).
- Semantic HTML first; ARIA only to fill gaps. Real labels (not placeholders).
- Target size ≥ **24×24px**; don't convey meaning by color alone.
- Honor **`prefers-reduced-motion`** — always provide a reduced/no-motion path.

## Completeness
- Specify **every state** for every component: default, hover, focus, active,
  disabled, **loading/skeleton**, **empty**, **error**, success. The happy path
  alone is an incomplete design.

## Layout & type
- One **spacing scale** (e.g. 4px base) and one **type scale** — used consistently.
- Line length **45–75ch**; deliberate hierarchy; whitespace is a feature, not waste.
- **Mobile-first**, responsive at real breakpoints; test the smallest screen first.

## Motion
- Motion has a **system**: a duration scale (e.g. 150/250/400ms) and an easing
  scale. Implemented with **framer-motion**. Motion must be **purposeful** (it
  explains a change) — never decorative noise, never blocking.

## Performance (design ↔ Core Web Vitals)
- Media/embeds carry explicit **width/height** (no **CLS**). The **LCP** element is
  light and prioritized. Fonts use `font-display: swap`; avoid heavy webfonts.
- A design that regresses CWV is not shipped — coordinate with the `seo` pack.

## Reuse
- Check existing tokens/components and the **21st.dev catalog** before creating new
  UI. Never ship a duplicate of an existing component.

## Governance
- Nothing ships that violates this file or `anti-patterns.md`. Contrast, keyboard
  and CLS are **verified**, not assumed (see `checklists.md`).
