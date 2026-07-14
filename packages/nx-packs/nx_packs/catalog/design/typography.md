# Typography

Type carries most of the UI's usability. Get the scale and the measure right and
the interface reads as designed.

## Type scale
Use a **modular scale** (ratio ~1.125–1.25) rather than arbitrary sizes:

| Token | Size | Use |
|-------|------|-----|
| xs | 12px | captions, meta |
| sm | 14px | secondary, labels |
| base | 16px | **body (never below 16 for body)** |
| lg | 18px | lead paragraph |
| xl–2xl | 20–24px | section headings |
| 3xl–4xl | 30–36px+ | page/hero headings |

## Pairing
- One family is often enough. If pairing: **contrast the roles** (a distinctive
  display face for headings + a highly legible workhorse for body) — never two
  faces that look almost the same.
- Justify the pairing (tone, x-height, legibility at size), don't pick by vibe.
- Load only the weights you use; `font-display: swap`; prefer variable fonts.

## Readability
- **Measure 45–75ch** for body text (`max-w-prose`).
- Line-height: ~1.5 body, ~1.2 headings. Tighter tracking on large headings only.
- Left-align body text; avoid justified text on the web.
- Hierarchy must be obvious **at a glance** — size, weight and color, not just size.

## Rules
- Body text ≥ **16px**; never sacrifice legibility for density.
- Don't use more than ~3 weights and ~5 sizes on a screen.
- Headings are semantic (`h1`→`h6`) **and** visual — don't fake hierarchy with
  styled `div`s.
