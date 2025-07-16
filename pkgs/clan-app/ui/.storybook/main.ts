import { mergeConfig } from "vite";
import type { StorybookConfig } from "@kachurun/storybook-solid-vite";

const config: StorybookConfig = {
  framework: "@kachurun/storybook-solid-vite",
  stories: ["../src/**/*.mdx", "../src/**/*.stories.tsx"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-docs",
    "@storybook/addon-a11y",
  ],
  async viteFinal(config) {
    return mergeConfig(config, {
      define: { "process.env": {} },
    });
  },
  core: {
    disableTelemetry: true,
  },
  typescript: {
    reactDocgen: "react-docgen-typescript",
    reactDocgenTypescriptOptions: {
      shouldExtractLiteralValuesFromEnum: true,
      // 👇 Default prop filter, which excludes props from node_modules
      propFilter: (prop: any) =>
        prop.parent ? !/node_modules/.test(prop.parent.fileName) : true,
    },
  },
};

export default config;
