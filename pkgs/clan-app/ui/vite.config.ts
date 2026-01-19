import { defineConfig } from "vite";
import wyw from "@wyw-in-js/vite";
import solidPlugin from "vite-plugin-solid";
import solidSvg from "vite-plugin-solid-svg";
import { patchCssModules } from "vite-css-modules";

export default defineConfig(({ mode }) => {
  return {
    resolve: {
      alias: {
        "@": new URL("src", import.meta.url).pathname,
        "$clan-api-client": new URL(
          "src/models/api/clan/client/" +
            (process.env.VITE_CLAN_API_BASE ? "http" : "rpc"),
          import.meta.url,
        ).pathname,
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
      solidSvg({
        svgo: {
          enabled: true,
          svgoConfig: {
            plugins: ["removeXMLNS"],
          },
        },
      }),
      patchCssModules({ generateSourceTypes: true }),
    ],
    server: {
      port: 3000,
    },
    build: {
      target: "safari11",
      modulePreload: false,
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
