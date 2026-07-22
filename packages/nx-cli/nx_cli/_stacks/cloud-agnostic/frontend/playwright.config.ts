import { defineConfig, devices } from "@playwright/test";

// Visual & responsive QA for {{project_title}}. Drives the running frontend across
// the device matrix (visual-qa pack). Start it first on a free port — `nxai port`.
const PORT = process.env.FRONTEND_PORT || "{{frontend_port}}";
const BASE_URL = process.env.BASE_URL || `http://localhost:${PORT}`;

export default defineConfig({
  testDir: "./tests/visual",
  snapshotDir: "./tests/visual/__screenshots__",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  // The non-negotiable six viewports + named devices (see visual-qa/device-matrix.md).
  projects: [
    { name: "small-phone-360", use: { viewport: { width: 360, height: 640 } } },
    { name: "modern-phone-390", use: { viewport: { width: 390, height: 844 } } },
    { name: "tablet-portrait-768", use: { viewport: { width: 768, height: 1024 } } },
    { name: "tablet-landscape-1024", use: { viewport: { width: 1024, height: 768 } } },
    { name: "laptop-1366", use: { viewport: { width: 1366, height: 768 } } },
    { name: "desktop-1920", use: { viewport: { width: 1920, height: 1080 } } },
    { name: "iphone-se", use: { ...devices["iPhone SE"] } },
    { name: "iphone-15", use: { ...devices["iPhone 15 Pro"] } },
    { name: "pixel-9", use: { ...devices["Pixel 7"] } },
    { name: "ipad", use: { ...devices["iPad (gen 7)"] } },
    { name: "webkit-phone", use: { ...devices["iPhone 15"], browserName: "webkit" } },
  ],
  // Auto-start the dev server for the run (reuses a running one locally).
  webServer: {
    command: `npm run dev -- --port ${PORT}`,
    url: BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
