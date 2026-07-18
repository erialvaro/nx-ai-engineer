# UI Reverse Engineering — Engineering Pack

The knowledge standard for **reverse-engineering a website's UI/UX and rebuilding
it cleanly**. It feeds the **`reverse-engineer` agent** (and designer/frontend/
architect) via the Engineering Contract: the agent executes, this pack holds the
standard.

The loop it encodes:

```
Website → Playwright (navega como usuário) → captura HTML · CSS · screenshots
(desktop + mobile) · assets · fontes · SVG/ícones · links · comportamento
→ análise → design system → rebuild em React + Vite + Tailwind + shadcn/ui
(componentizado, refatorado, NÃO cópia literal)
```

## What it covers
- **[policies.md](policies.md)** — non-negotiable rules. **Legal gate** (own or
  authorized only), refactor-never-copy, keep layout & UX only, replace
  third-party assets, a11y + responsive baseline, record provenance.
- **[capture-playbook.md](capture-playbook.md)** — the Playwright recipes: launch,
  goto, full-page + component screenshots (desktop + mobile), extract HTML, CSS,
  images, fonts, SVG/icons, links; record interactions; `codegen`; and the
  **Playwright MCP** flow (agent drives the browser directly).
- **[patterns.md](patterns.md)** — the capture → analyze → rebuild pipeline and
  the design-system extraction method.
- **[anti-patterns.md](anti-patterns.md)** — pixel-cloning, literal HTML dumps,
  scraping behind auth, ignoring robots/ToS, reusing trademarked assets.
- **[checklists.md](checklists.md)** — capture checklist + rebuild checklist.
- **[architecture.md](architecture.md)** — how a capture run is organized on disk
  and handed to the rebuild.
- **[context.md](context.md)** — the compact brief injected into the agent.

## The bar
The job is done when the rebuilt project **reproduces the layout and UX** of the
source, but as **clean, componentized, accessible, responsive** code that a
senior engineer would ship — with **no literal copy**, **no unlicensed assets**,
a **documented design system**, and the **authorization basis on record**.
