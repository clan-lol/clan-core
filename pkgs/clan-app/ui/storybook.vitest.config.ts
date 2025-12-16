import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";
import { storybookTest } from "@storybook/addon-vitest/vitest-plugin";
import { playwright } from "@vitest/browser-playwright";
import path from "node:path";

export default defineConfig((configEnv) =>
  mergeConfig(
    viteConfig(configEnv),
    defineConfig({
      plugins: [
        // The plugin will run tests for the stories defined in your Storybook config
        // See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
        storybookTest({
          configDir: path.resolve(__dirname, ".storybook"),
        }),
      ],
      test: {
        browser: {
          // Enable browser-based testing for UI components
          enabled: true,
          headless: true,
          provider: playwright(),
          instances: [
            {
              // Ideally we should use webkit to match clan-app, but inside a
              // sandboxed nix build, webkit takes forever to finish
              // launching. Chromium randomly closes itself during testing, as
              // reported here:
              // https://github.com/vitest-dev/vitest/discussions/7981
              //
              // Firefox is the only browser that can reliably finish the
              // tests. We want to test storybook only, and the differences
              // between browsers are probably negligible to us
              browser: "firefox",
            },
          ],
        },
        setupFiles: [".storybook/vitest.setup.ts"],
      },
    }),
  ),
);
