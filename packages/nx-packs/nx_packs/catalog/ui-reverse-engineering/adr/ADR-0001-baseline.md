# ADR-0001 — UI reverse-engineering baseline (capture → rebuild, never copy)

- **Status:** Accepted
- **Context:** Rebuilding a website's UI is fastest when you capture the real,
  rendered result (HTML, CSS, screenshots, behavior) with a real browser and then
  re-implement it as clean components — instead of guessing from a design file or
  pasting scraped markup. This is powerful and easy to misuse, so it needs a hard
  legal/ethical gate and a "refactor, never copy" rule.

## Decision
Adopt this pack's standard for any UI reverse-engineering / redesign / migration:
- **Legal gate first** — only sites the user owns or is authorized to rebuild;
  respect robots.txt/ToS; no auth/paywall bypass; record the authorization basis.
- **Capture with Playwright** (prefer the Playwright MCP) — full-page screenshots
  **desktop + mobile**, rendered HTML, CSS, assets/fonts/SVG/icons, links, and key
  interactions, in a self-contained capture folder with `meta.json`.
- **Design system before code** — distill tokens (color/type/space/radii/shadow/
  breakpoints) and a component inventory, written down first.
- **Rebuild, never copy** — React + Vite + Tailwind + shadcn/ui by default;
  role-named reusable components; content as data; tokens over magic numbers. No
  literal HTML/CSS and no unlicensed third-party IP shipped.
- **Improve, don't inherit flaws** — fix a11y, responsiveness, semantics,
  performance; keep provenance and deviations on record.

## Consequences
- ➕ Faithful layout/UX rebuilt as clean, accessible, responsive, componentized
  code a senior engineer would ship.
- ➕ Quality and legality are checkable (gate, capture checklist, rebuild + a11y
  checklists, provenance) — not a matter of taste.
- ➖ Requires the authorization gate and a disciplined capture→system→rebuild loop;
  enforced via the `reverse-engineer` agent's checklist and this pack's
  `policies.md` / `anti-patterns.md`.
