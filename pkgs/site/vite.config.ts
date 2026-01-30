import clanmd from "vite-plugin-clanmd";
import configPlugin from "vite-plugin-config";
import { defineConfig } from "vite";
import { pagefind } from "vite-plugin-pagefind";
import siteConfig from "./site.config.ts";
import { sveltekit } from "@sveltejs/kit/vite";

export default defineConfig({
  server: {
    fs: {
      allow: ["./packages"],
    },
  },
  plugins: [
    sveltekit(),
    configPlugin({
      config: siteConfig,
    }),
    clanmd({
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
