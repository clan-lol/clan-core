import { createRequire } from "module";
import { dirname, join } from "path";
import { mergeConfig } from "vite";
import type { StorybookConfig } from "@kachurun/storybook-solid-vite";

const require = createRequire(import.meta.url);
const getAbsolutePath = (pkg: string) =>
  dirname(require.resolve(join(pkg, "package.json")));

const config: StorybookConfig = {
  stories: ["../src/components/**/*.mdx", "../src/components/**/*.stories.tsx"],
  addons: [
    getAbsolutePath("@storybook/addon-links"),
    getAbsolutePath("@storybook/addon-essentials"),
    getAbsolutePath("@chromatic-com/storybook"),
    getAbsolutePath("@storybook/addon-interactions"),
  ],
  framework: {
    name: "@kachurun/storybook-solid-vite",
    options: {},
  },
  async viteFinal(config) {
    return mergeConfig(config, {
      define: { "process.env": {} },
    });
  },
  docs: {
    autodocs: "tag",
  },
};

export default config;
