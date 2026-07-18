# Architecture — capture run layout & handoff

A capture run is a self-contained folder; the rebuild reads from it.

```
capture/<domain>/<YYYY-MM-DD>/
  meta.json            # source URLs, viewports, capture date, AUTHORIZATION basis
  desktop/
    home.png           # full-page, 1920×1080
    <page>.png
    state-*.png        # interaction states (menu open, modal, form filled)
    components/<role>.png
  mobile/
    home.png           # full-page, 390×844
    <page>.png
  html/<page>.html     # rendered DOM (reference, not source)
  css/styles.css       # concatenated stylesheets (cross-origin skipped)
  assets/
    images/            # only assets you are entitled to reuse
    fonts/
    svg/
  design-system.md     # the distilled system (written before rebuild)
```

`meta.json` (minimum):
```json
{
  "sources": ["https://site.com", "https://site.com/pricing"],
  "capturedAt": "2026-07-18",
  "viewports": [{ "w": 1920, "h": 1080 }, { "w": 390, "h": 844 }],
  "authorization": "owner | client-contract | permitted-inspiration",
  "notes": "assets with third-party IP flagged, not shipped"
}
```

## Handoff to the rebuild
1. The **designer** reads screenshots + `design-system.md` → confirms/refines the
   token system and component inventory.
2. The **frontend** builds the components (React + Vite + Tailwind + shadcn/ui)
   against the tokens, content as data.
3. The **architect** validates structure/boundaries; the rebuild checklist and
   a11y checklist gate delivery.

Keep the capture folder out of the shipped app (it's reference); the rebuilt
project is the deliverable.
