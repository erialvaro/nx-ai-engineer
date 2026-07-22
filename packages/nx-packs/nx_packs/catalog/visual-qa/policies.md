# Policies — Visual & Responsive QA (binding gates)

These are **release gates**. A change to any user-facing UI does not pass until
all of them hold on the key routes, across the device matrix, in light AND dark.

## Layout & responsiveness

1. **No horizontal overflow.** `document.documentElement.scrollWidth` must be
   `<=` the viewport width on every tested viewport. Horizontal scrollbars on a
   page are a defect.
2. **Nothing clipped or off-screen.** Every interactive element (nav items,
   buttons, CTAs, form controls, menus) is fully within the viewport and
   reachable. No element is cut off by a container with the wrong overflow.
3. **Mobile-first, tested small→large.** The layout is verified from 360px up.
   Content reflows; it does not require zoom or sideways scroll.
4. **Touch targets >= 44x44px** on touch viewports (>= 24px minimum everywhere,
   WCAG 2.2 Target Size); adequate spacing between tap targets.
5. **Safe areas honored** on notched devices (no content under the notch / home
   indicator).

## Accessibility (WCAG 2.2 AA)

6. **Contrast** >= 4.5:1 for body text, >= 3:1 for large text and UI/graphical
   components — verified in **both** themes.
7. **Visible focus** on every interactive element; full keyboard reachability;
   logical tab order.
8. **Semantics + labels** — roles/labels present; images have alt; forms have
   associated labels. `prefers-reduced-motion` is honored.

## Performance / Core Web Vitals

9. **Lighthouse category scores >= 95** — Performance, Accessibility,
   Best-Practices and SEO — on the key routes (mobile profile is the reference).
10. **CLS < 0.1** and **no unsized media** (img/video/iframe have width/height or
    aspect-ratio); **LCP** in the "good" band.

## Process

11. **Real running app.** Tests drive the live dev/preview URL (port verified),
    never a static mock.
12. **QA does not edit product source.** `visual-qa` writes test specs, configs
    and baselines and reports defects with before/after screenshots; the fix is
    made by the owning developer and then **re-verified green**.
13. **Baselines are approved deliberately.** BackstopJS diffs are reviewed;
    intended visual changes are re-approved, unintended ones are regressions.
14. **Gates run in CI.** Playwright + Lighthouse CI enforce these thresholds on
    every PR — a regression blocks the merge.
