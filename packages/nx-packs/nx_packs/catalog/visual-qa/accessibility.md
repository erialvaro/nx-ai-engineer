# Accessibility Gates (WCAG 2.2 AA)

Verified visually and programmatically, in **light and dark**, on every key route.
Playwright + `@axe-core/playwright` automates most of it; contrast and focus are
also eyeballed in the screenshots.

## Contrast
- Body text >= **4.5:1**; large text (>= 24px or 19px bold) and UI/graphical
  components >= **3:1**.
- Check **both themes** — dark mode is where contrast quietly fails.
- Never convey state by color alone (add icon/text).

## Keyboard & focus
- Every interactive element is reachable by Tab in a logical order.
- **Visible focus** ring on each (never `outline: none` without a replacement).
- No keyboard traps; Esc closes modals; focus is managed on open/close.

## Semantics & labels
- Landmarks (`header`/`nav`/`main`/`footer`), headings in order (one `h1`).
- Images have meaningful `alt` (or empty alt if decorative).
- Every form control has an associated `<label>`; errors are announced.
- Interactive controls use real semantics (`button`/`a`) or correct ARIA roles.

## Motion & targets
- Honor `prefers-reduced-motion` — no essential info conveyed only by motion.
- Target size >= 24px (WCAG 2.2); >= 44px on touch, with spacing.

## Automated check (in the Playwright spec)
```ts
import AxeBuilder from "@axe-core/playwright";
const results = await new AxeBuilder({ page })
  .withTags(["wcag2a", "wcag2aa", "wcag22aa"]).analyze();
expect(results.violations).toEqual([]);
```
Axe catches the machine-checkable subset; the device-matrix screenshots and the
Lighthouse Accessibility score (>= 95) cover the rest.
