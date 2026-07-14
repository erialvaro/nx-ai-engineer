# Color

## Palette with roles (not a rainbow)
Design **roles**, not colors:

- `background` / `foreground` — the page
- `card` / `popover` (+ their foregrounds) — surfaces
- `muted` (+ foreground) — secondary text, subtle fills
- `primary` (+ foreground) — the one action that matters
- `secondary` / `accent` — supporting
- `destructive` (+ foreground) — irreversible actions
- `border` / `input` / `ring` — structure and focus

A restrained palette (1 primary + neutrals + 1 destructive) beats a colorful one.
Use color to **direct attention**, not to decorate.

## Contrast is a gate (WCAG 2.2)
| Content | Minimum |
|---------|---------|
| Body text | **4.5:1** |
| Large text (≥ 18.66px bold / 24px) | **3:1** |
| UI components & graphical objects (borders, icons, focus ring, chart marks) | **3:1** |

- **Verify** with a contrast checker — in **both** light and dark. Never eyeball.
- Muted text is the usual failure: `muted-foreground` on `background` must still
  pass 4.5:1 if it carries meaning.

## Dark mode
- Dark is **designed**, not inverted. Pure black (#000) + pure white is harsh —
  use a deep neutral background and a slightly off-white foreground.
- Elevation in dark comes from **lighter surfaces**, not bigger shadows.
- Re-check every contrast pair in dark; saturated colors often need a lighter tint.

## Rules
- **Never convey meaning by color alone** (add an icon, label, or pattern).
- Keep semantic colors semantic: destructive is only for destructive.
- Charts: use the `dataviz` standard (accessible, consistent categorical palette).
