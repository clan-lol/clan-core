import clanmd from "vite-plugin-clanmd";
import config from "./src/config/index.ts";
import { defineConfig } from "vite";
import { pagefind } from "vite-plugin-pagefind";
import { sveltekit } from "@sveltejs/kit/vite";

export default defineConfig({
  server: {
    fs: {
      allow: ["./packages"],
    },
  },
  plugins: [
    sveltekit(),
    clanmd({
      codeLightTheme: config.docs.codeLightTheme,
      codeDarkTheme: config.docs.codeDarkTheme,
      minLineNumberLines: config.docs.minLineNumberLines,
      maxTocExtractionDepth: config.docs.maxTocExtractionDepth,
    }),
    pagefind({
      outputDirectory: "build",
      assetsDirectory: "static",
    }),
  ],
});
