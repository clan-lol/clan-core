import type { StorybookConfig } from "storybook-solidjs-vite";

export default {
  framework: "storybook-solidjs-vite",
  stories: ["../src/**/*.mdx", "../src/**/*.stories.tsx"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-docs",
    "@storybook/addon-a11y",
    {
      name: "@storybook/addon-vitest",
      options: {
        cli: false,
      },
    },
  ],
  core: {
    disableTelemetry: true,
  },
} satisfies StorybookConfig;
