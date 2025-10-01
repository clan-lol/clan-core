import path from "node:path";
import { fileURLToPath } from "node:url";

import solid from "vite-plugin-solid";
import { defineConfig, mergeConfig } from "vitest/config";
// @ts-expect-error the type is a bit funky, but it's working
import { storybookTest } from "@storybook/addon-vitest/vitest-plugin";

const dirname =
  typeof __dirname !== "undefined"
    ? __dirname
    : path.dirname(fileURLToPath(import.meta.url));

import viteConfig from "./vite.config";

const browser = process.env.BROWSER || "chromium";

export default mergeConfig(
  viteConfig,
  defineConfig({
    plugins: [solid()],
    test: {
      projects: [
        {
          test: {
            name: "unit",
          },
        },
        {
          extends: path.join(dirname, "vite.config.ts"),
          plugins: [
            // The plugin will run tests for the stories defined in your Storybook config
            // See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
            storybookTest({
              configDir: path.join(dirname, ".storybook"),
            }),
          ],
          test: {
            name: "storybook",
            browser: {
              // Enable browser-based testing for UI components
              enabled: true,
              headless: true,
              provider: "playwright",
              instances: [
                {
                  browser: "chromium",
                  launch: {
                    // we specify this explicitly to avoid the version matching that playwright tries to do
                    executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
                  },
                },
              ],
            },
            // This setup file applies Storybook project annotations for Vitest
            // More info at: https://storybook.js.org/docs/api/portable-stories/portable-stories-vitest#setprojectannotations
            setupFiles: [".storybook/vitest.setup.ts"],
          },
        },
      ],
    },
  }),
);
