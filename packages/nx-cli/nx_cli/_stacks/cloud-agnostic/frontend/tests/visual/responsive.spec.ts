import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

// Key routes to verify. Add your real routes here as the app grows.
const ROUTES = ["/"];

for (const route of ROUTES) {
  test.describe(`visual QA ${route}`, () => {
    test("no horizontal overflow", async ({ page }) => {
      await page.goto(route, { waitUntil: "networkidle" });
      const overflows = await page.evaluate(() => {
        const el = document.documentElement;
        return el.scrollWidth > el.clientWidth + 1; // 1px tolerance
      });
      expect(overflows, "page scrolls horizontally").toBeFalsy();
    });

    test("primary landmarks are visible in-viewport", async ({ page }) => {
      await page.goto(route, { waitUntil: "networkidle" });
      // Header/nav (if present) must sit inside the viewport, not clipped off-screen.
      const nav = page.locator("header, nav").first();
      if (await nav.count()) {
        const box = await nav.boundingBox();
        const vw = page.viewportSize()!.width;
        expect(box).not.toBeNull();
        expect(box!.x).toBeGreaterThanOrEqual(-1);
        expect(box!.x + box!.width).toBeLessThanOrEqual(vw + 1);
      }
    });

    test("full-page screenshot (visual baseline)", async ({ page }, testInfo) => {
      await page.goto(route, { waitUntil: "networkidle" });
      await expect(page).toHaveScreenshot(
        `${testInfo.project.name}${route === "/" ? "/home" : route}.png`,
        { fullPage: true, maxDiffPixelRatio: 0.02 },
      );
    });

    test("no critical accessibility violations", async ({ page }) => {
      await page.goto(route, { waitUntil: "networkidle" });
      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
        .analyze();
      const serious = results.violations.filter(
        (v) => v.impact === "critical" || v.impact === "serious",
      );
      expect(serious, JSON.stringify(serious.map((v) => v.id))).toEqual([]);
    });
  });
}
