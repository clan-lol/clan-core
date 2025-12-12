import { defineConfig } from "vite";
import wyw from "@wyw-in-js/vite";
import solidPlugin from "vite-plugin-solid";
import solidSvg from "vite-plugin-solid-svg";
import { patchCssModules } from "vite-css-modules";
import path from "node:path";
import { exec } from "child_process";

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

export default defineConfig(({ mode }) => {
  return {
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./"),
        // Different script can be used based on different env vars
        "@api/clan/client": path.resolve(
          __dirname,
          "./src/api/clan/client-call",
        ),
      },
    },
    base: "./",
    optimizeDeps: {
      include: ["debug", "extend"],
    },
    plugins: [
      solidPlugin(),
      wyw({
        displayName: mode === "development",
        babelOptions: {
          presets: ["@babel/preset-typescript", "solid"],
        },
      }),
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
  };
});
