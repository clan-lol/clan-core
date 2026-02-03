import { defineConfig } from "vite";
import markdown from "@clan/vite-plugin-markdown";
import { pagefind } from "vite-plugin-pagefind";
import siteConfig from "./clan-site.config.ts";
import { sveltekit } from "@sveltejs/kit/vite";
import valuePlugin from "vite-plugin-value";

export default defineConfig({
  server: {
    fs: {
      allow: ["./packages"],
    },
  },
  plugins: [
    sveltekit(),
    valuePlugin({
      name: "$config",
      value: siteConfig,
    }),
    markdown({
      codeLightTheme: siteConfig.docs.codeLightTheme,
      codeDarkTheme: siteConfig.docs.codeDarkTheme,
      minLineNumberLines: siteConfig.docs.minLineNumberLines,
      maxTocExtractionDepth: siteConfig.docs.maxTocExtractionDepth,
      /* eslint-disable @typescript-eslint/naming-convention */
      linkResolves: {
        "src/docs": `/docs/${siteConfig.ver}`,
      },
      /* eslint-enable @typescript-eslint/naming-convention */
    }),
    pagefind({
      outputDirectory: "build",
      assetsDirectory: "static",
    }),
  ],
});
