import type { Preview } from "@storybook/react";

// Device-matrix viewports mirrored into Storybook so component stories can be
// checked at the same widths the visual-qa spec uses.
const preview: Preview = {
  parameters: {
    controls: { matchers: { color: /(background|color)$/i, date: /Date$/i } },
    a11y: { config: { rules: [] } },
    viewport: {
      viewports: {
        phone360: { name: "Phone 360", styles: { width: "360px", height: "640px" } },
        phone390: { name: "Phone 390", styles: { width: "390px", height: "844px" } },
        tablet768: { name: "Tablet 768", styles: { width: "768px", height: "1024px" } },
        laptop1366: { name: "Laptop 1366", styles: { width: "1366px", height: "768px" } },
        desktop1920: { name: "Desktop 1920", styles: { width: "1920px", height: "1080px" } },
      },
    },
  },
};

export default preview;
