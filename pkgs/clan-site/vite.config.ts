import cssnano from "cssnano";
import { defineConfig } from "vite";
import markdown from "@clan/vite-plugin-markdown";
import pagefind from "@clan/vite-plugin-pagefind";
import postcssGlobalData from "@csstools/postcss-global-data";
import postcssPresetEnv from "postcss-preset-env";
import siteConfig from "./clan-site.config.ts";
import { sveltekit } from "@sveltejs/kit/vite";
import svg from "@poppanator/sveltekit-svg";
import valuePlugin from "vite-plugin-value";

export default defineConfig(({ mode }) => ({
  server: {
    fs: {
      allow: ["./packages"],
    },
  },
  css: {
    postcss: {
      plugins: [
        // This is needed to resolve things like custom media
        // https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-global-data#postcss-global-data-
        postcssGlobalData({
          files: [
            "./src/css/custom-media.css",
            "./src/css/custom-properties.css",
          ],
        }),
        postcssPresetEnv(),
        ...(mode === "development" ? [] : [cssnano({ preset: "default" })]),
      ],
    },
  },
  plugins: [
    sveltekit(),
    svg({
      svgoOptions: {
        plugins: ["removeXMLNS"],
      },
    }),
    valuePlugin({
      specifier: "$config",
      value: siteConfig,
    }),
    markdown({
      codeLightTheme: siteConfig.codeLightTheme,
      codeDarkTheme: siteConfig.codeDarkTheme,
      minLineNumberLines: siteConfig.codeMinLineNumberLines,
      maxTocExtractionDepth: siteConfig.maxTocExtractionDepth,
      linkResolves: {
        [siteConfig.docsDir]: siteConfig.docsBase,
      },
    }),
    pagefind({
      pluginInstance: "docs",
      siteDir: `build${siteConfig.docsBase}`,
      staticDir: "static",
      assetsDir: `build/_assets/${siteConfig.version}`,
      bundleDir: "_pagefind/docs",
      base: siteConfig.docsBase,
    }),
  ],
}));
