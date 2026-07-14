# Layout & spacing

## One spacing scale
Base **4px**, geometric-ish: `4, 8, 12, 16, 24, 32, 48, 64, 96`. Every margin,
padding and gap comes from it. No `27px`.

- **Space relates**: elements that belong together sit closer (proximity is the
  cheapest grouping tool you have).
- Use **gap** (flex/grid) over margins where possible — spacing belongs to the
  container, not the child.

## Grid & structure
- Pick a grid (12-col on desktop is fine) and hold to it. Content max-width for
  reading (~65–75ch); wider only for dashboards/tables.
- **Vertical rhythm**: consistent section padding; don't hand-tune each block.
- **Whitespace is a feature.** Crowding is the most common self-inflicted wound.

## Responsive (mobile-first)
- Design the **smallest screen first**, then add breakpoints where the layout
  actually breaks — not at arbitrary device widths.
- Prefer **fluid** type/space (`clamp()`) over many breakpoints.
- Touch targets ≥ **24×24px** (44px is safer for primary actions); no hover-only
  affordances on touch.

## Hierarchy
- One clear focal point per screen (usually the primary action or the key data).
- Size, weight, color and space create hierarchy — in that order. Borders last.
- Alignment: pick one and be ruthless; misalignment reads as "broken", not "playful".

## Layouts that work
- **Bento grid** for feature/marketing overviews; **card grid** for collections;
  **sidebar + content** for apps; **hero + proof + CTA** for landing.
- Tables: sticky header, aligned numerics (tabular figures), zebra only if it helps.
