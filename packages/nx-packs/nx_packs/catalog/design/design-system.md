# Design system — tokens as the single source of truth

A design system is not a component folder. It is a **contract of tokens** that
components consume, so the UI stays consistent as it grows.

## The token layers
1. **Primitives** (raw values): `blue-500`, `space-4`, `text-lg`, `radius-md`.
2. **Semantic** (roles — what components actually use):
   `--background`, `--foreground`, `--card`, `--muted`, `--primary`,
   `--primary-foreground`, `--border`, `--ring`, `--destructive`.
3. **Component tokens** (only when justified): `--button-height-sm`.

Components reference **semantic** tokens — never primitives, never magic values.

## Token families (define all of them)
| Family | Examples |
|--------|----------|
| Color | bg / surface / fg / muted / primary / secondary / destructive / border / ring |
| Type | family, scale (xs→4xl), weight, line-height, letter-spacing |
| Space | 4px base scale: 1,2,3,4,6,8,12,16,24 |
| Radius | sm / md / lg / full |
| Shadow | sm / md / lg (subtle; elevation, not decoration) |
| Z-index | base / dropdown / sticky / overlay / modal / toast |
| Motion | duration (fast/base/slow) + easing (standard/enter/exit) |

## Where they live (the stack we default to)
- **CSS variables** in `globals.css` (`:root` + `.dark`) — the source of truth.
- **Tailwind config** maps utilities to those variables.
- **shadcn/ui** `components.json` wires the component library to the same tokens.
- Publish/share them with **`21st-design-sync`**; pull components that already
  consume them with **`21st-cli-use`**.

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --primary: 221 83% 53%;
  --primary-foreground: 0 0% 100%;
  --muted: 210 40% 96%;
  --border: 214 32% 91%;
  --ring: 221 83% 53%;
  --radius: 0.5rem;
}
.dark {
  --background: 222 47% 11%;
  --foreground: 210 40% 98%;
  /* dark is DESIGNED — not a naive inversion */
}
```

## Rules
- **Dark is designed**, not inverted: re-check contrast, elevation and shadows.
- Add a token only when it is reused; otherwise it is a one-off, not a system.
- Every new component must be expressible **entirely in tokens**. If it isn't, the
  system is missing a token — add it deliberately.
