import { defineConfig } from "vite";
import markdown from "@clan/vite-plugin-markdown";
import pagefind from "@clan/vite-plugin-pagefind";
import siteConfig from "./clan-site.config.ts";
import { sveltekit } from "@sveltejs/kit/vite";
import svg from "@poppanator/sveltekit-svg";
import valuePlugin from "vite-plugin-value";

export default defineConfig({
  server: {
    fs: {
      allow: ["./packages"],
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
});
