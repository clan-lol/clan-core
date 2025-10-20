import { defineConfig } from "vite";
import wyw from "@wyw-in-js/vite";
import solidPlugin from "vite-plugin-solid";
import solidSvg from "vite-plugin-solid-svg";
import { patchCssModules } from "vite-css-modules";
import path from "node:path";
import { exec } from "child_process";
// @ts-expect-error the type is a bit funky, but it's working
import { storybookTest } from "@storybook/addon-vitest/vitest-plugin";

// watch also clan-cli to catch api changes
const clanCliDir = path.resolve(__dirname, "../../clan-cli");

function regenPythonApiOnFileChange() {
  return {
    name: "run-python-script-on-change",
    handleHotUpdate() {
      exec("reload-python-api.sh", (err, stdout, stderr) => {
        if (err) {
          console.error(`reload-python-api.sh error:\n${stderr}`);
        }
      });
    },
    configureServer(server: import("vite").ViteDevServer) {
      server.watcher.add([clanCliDir]);
    },
  };
}

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
      // Different script can be used based on different env vars
      "@api/clan/client": path.resolve(__dirname, "./src/api/clan/client-call"),
    },
  },
  base: "./",
  optimizeDeps: {
    include: ["debug", "extend"],
  },
  plugins: [
    /*
    Uncomment the following line to enable solid-devtools.
    For more info see https://github.com/thetarnav/solid-devtools/tree/main/packages/extension#readme
    */
    solidPlugin(),
    wyw(),
    solidSvg(),
    regenPythonApiOnFileChange(),
    patchCssModules({ generateSourceTypes: true }),
  ],
  server: {
    port: 3000,
  },
  build: {
    target: "safari11",
    modulePreload: false,
    //  assetsDi
    manifest: true,
    // Inline everything: TODO
    // Detect file:///assets requests and point to the correct directory in webview
    rollupOptions: {
      output: {
        format: "iife",
        // entryFileName: ""
        // inlineDynamicImports: true,
      },
    },
    // assetsInlineLimit: 0,
  },
  test: {
    projects: [
      {
        test: {
          name: "unit",
        },
      },
      {
        extends: path.resolve(__dirname, "vite.config.ts"),
        plugins: [
          // The plugin will run tests for the stories defined in your Storybook config
          // See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
          storybookTest({
            configDir: path.resolve(__dirname, ".storybook"),
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
                browser: "webkit",
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
});
