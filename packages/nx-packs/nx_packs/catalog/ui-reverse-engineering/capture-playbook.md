# Capture Playbook — Playwright recipes

Practical recipes for the capture stage. Two ways to drive the browser:
**(A) scripts** (deterministic, batch) or **(B) the Playwright MCP** (the agent
drives the browser live). Prefer MCP when available; fall back to scripts.

Confirm the **legal gate** (policies §0) before capturing anything.

## Setup
```bash
npm init -y
npm install playwright
npx playwright install
```

## Recommended run layout (see architecture.md)
```
capture/<domain>/<date>/
  desktop/  home.png, <page>.png, components/<name>.png
  mobile/   home.png, <page>.png
  html/     <page>.html
  css/      styles.css
  assets/   images/  fonts/  svg/
  meta.json (source urls, viewports, date, authorization basis)
```

## 1. Launch + full-page screenshot + HTML
```js
const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto("https://site.com", { waitUntil: "networkidle" });
  await page.screenshot({ path: "desktop/home.png", fullPage: true });
  const html = await page.content();               // DOM renderizado
  require("fs").writeFileSync("html/home.html", html);
  await browser.close();
})();
```

## 2. Mobile viewport (always capture both)
```js
const page = await browser.newPage({
  viewport: { width: 390, height: 844 }, deviceScaleFactor: 2,
  isMobile: true, hasTouch: true,
});
await page.goto("https://site.com", { waitUntil: "networkidle" });
await page.screenshot({ path: "mobile/home.png", fullPage: true });
```

## 3. Extract CSS (all stylesheets, cross-origin-safe)
```js
const css = await page.evaluate(() =>
  [...document.styleSheets].map(sheet => {
    try { return [...sheet.cssRules].map(r => r.cssText).join("\n"); }
    catch { return ""; } // cross-origin sheet — skip
  }).join("\n")
);
```

## 4. Extract images, fonts, SVG, icons
```js
const images = await page.$$eval("img", els => els.map(i => i.currentSrc || i.src));
const bgImages = await page.evaluate(() =>
  [...document.querySelectorAll("*")]
    .map(el => getComputedStyle(el).backgroundImage)
    .filter(v => v && v !== "none"));
const fonts = await page.evaluate(() =>
  [...new Set([...document.querySelectorAll("*")].map(el => getComputedStyle(el).fontFamily))]);
const svgs = await page.$$eval("svg", els => els.map(s => s.outerHTML));
```
> Capture assets as **reference**. Do NOT ship logos/trademarked/licensed assets
> (policies §0) — download only what you are entitled to reuse.

## 5. Design tokens (sample computed styles, not raw CSS)
```js
const tokens = await page.evaluate(() => {
  const seen = { colors: new Set(), radii: new Set(), shadows: new Set(), sizes: new Set() };
  for (const el of document.querySelectorAll("body *")) {
    const s = getComputedStyle(el);
    seen.colors.add(s.color); seen.colors.add(s.backgroundColor);
    seen.radii.add(s.borderRadius); seen.shadows.add(s.boxShadow);
    seen.sizes.add(s.fontSize);
  }
  return Object.fromEntries(Object.entries(seen).map(([k, v]) => [k, [...v]]));
});
```
Cluster these into a token scale (see patterns.md → design-system extraction).

## 6. Crawl the main nav (a few pages, not the whole site)
```js
const links = await page.$$eval("nav a, header a", as =>
  [...new Set(as.map(a => a.href))].filter(h => h.startsWith(location.origin)));
// visit each, repeat steps 1–5. Cap it; respect rate limits (policies §0).
```

## 7. Per-component screenshots
```js
for (const sel of ["header", ".hero", ".card", "footer", "nav"]) {
  const el = await page.$(sel);
  if (el) await el.screenshot({ path: `desktop/components/${sel.replace(/[^\w]/g,"_")}.png` });
}
```

## 8. Record behavior / interactions
```js
await page.click("text=Entrar");
await page.fill("#email", "demo@example.com");
await page.screenshot({ path: "desktop/state-login.png" });
```
Or generate code by clicking through the site yourself:
```bash
npx playwright codegen https://site.com
```

## B. Playwright MCP (preferred with Claude Code)
Install the Playwright MCP so the agent drives the browser directly instead of
authoring scripts. Then a single instruction covers a whole capture:

> "Abra https://site.com, percorra as páginas do menu principal, capture
> screenshots em desktop e mobile, identifique componentes reutilizáveis, extraia
> HTML/CSS e produza um documento de design system (cores, tipografia,
> espaçamentos, componentes)."

And for the rebuild:

> "Analise o site capturado e crie um novo projeto React + Vite + Tailwind +
> shadcn/ui. Não copie o HTML; identifique padrões, separe em componentes
> reutilizáveis, melhore acessibilidade e responsividade, e organize em um design
> system."
