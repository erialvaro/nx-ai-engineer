import type { StorybookConfig } from "@storybook/nextjs";

// Storybook for {{project_title}} — isolate components and test their states
// (loading / empty / error / dark) per the visual-qa pack; pairs with BackstopJS.
const config: StorybookConfig = {
  stories: ["../**/*.stories.@(ts|tsx|mdx)"],
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-a11y",
    "@storybook/addon-viewport",
  ],
  framework: { name: "@storybook/nextjs", options: {} },
  staticDirs: ["../public"],
};

export default config;
