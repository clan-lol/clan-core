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
      codeLightTheme: siteConfig.docs.codeLightTheme,
      codeDarkTheme: siteConfig.docs.codeDarkTheme,
      minLineNumberLines: siteConfig.docs.minLineNumberLines,
      maxTocExtractionDepth: siteConfig.docs.maxTocExtractionDepth,
      linkResolves: {
        [siteConfig.docs.dir]: `/docs/${siteConfig.ver}`,
      },
    }),
    pagefind({
      pluginInstance: "docs",
      siteDir: `build${siteConfig.docs.base}`,
      staticDir: "static",
      assetsDir: `build/_assets/${siteConfig.ver}`,
      bundleDir: "_pagefind/docs",
      base: siteConfig.docs.base,
    }),
  ],
});
