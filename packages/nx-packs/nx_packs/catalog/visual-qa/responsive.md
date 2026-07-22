# Mobile-First Responsive Doctrine

What the `responsive` developer builds to, and what `visual-qa` verifies. The rule
of thumb: **design for 360px first, enhance upward** — never the reverse.

## Breakpoints (Tailwind defaults, mobile-first)

| Prefix | Min width | Target                         |
|--------|:---------:|--------------------------------|
| (base) | 0         | Phones — the default styles    |
| `sm`   | 640px     | Large phones / small tablets   |
| `md`   | 768px     | Tablets                        |
| `lg`   | 1024px    | Small laptops                  |
| `xl`   | 1280px    | Desktops                       |
| `2xl`  | 1536px    | Large desktops                 |

Base styles are the phone layout; each prefix *adds* as space grows. Avoid
desktop-first `max-*` overrides — they invert the cascade and cause overflow.

## No horizontal overflow — the top defect

- Never set fixed widths wider than the viewport; use `w-full`, `max-w-*`, `min-w-0`.
- Flex/grid children need `min-w-0` so long text can shrink instead of pushing
  the row wide.
- Long strings: `break-words` / `truncate`; tables scroll inside their own
  `overflow-x-auto` container — the **page** never scrolls sideways.
- Media: `max-w-full h-auto`. Absolute/fixed elements must not exceed the viewport.

## Fluid layout

- Prefer fluid units and `clamp()` for type and spacing over fixed px steps.
- Grids collapse columns as width shrinks (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`).
- Container queries for components that appear in different-width slots.

## Touch & safe areas

- Tap targets >= 44×44px on touch; generous spacing between them.
- Respect safe-area insets (`env(safe-area-inset-*)`) on notched devices.
- Hover-only affordances need a touch equivalent (no critical action behind `:hover`).

## Images & the fold

- Every `img`/`video`/`iframe` is sized (width/height or `aspect-ratio`) so it
  reserves space and never shifts the layout (CLS).
- Prioritize the LCP image; lazy-load below-the-fold.

## The mobile-first checklist the dev self-runs

- [ ] Built base → `sm` → `md` → `lg` (not the reverse)
- [ ] `min-w-0` on flex/grid children holding text
- [ ] No element wider than `100vw`; tables/code scroll inside their own box
- [ ] Media sized; LCP image prioritized
- [ ] Targets >= 44px; safe areas respected
- [ ] Verified on the device matrix before handing to `visual-qa`
