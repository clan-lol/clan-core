import { sveltekit } from "@sveltejs/kit/vite";
import { pagefind } from "vite-plugin-pagefind";
import { defineConfig } from "vite";
import markdown from "./src/vite-plugin-markdown";
import config from "./src/config";

export default defineConfig({
  plugins: [
    sveltekit(),
    markdown({
      codeLightTheme: config.docs.codeLightTheme,
      codeDarkTheme: config.docs.codeDarkTheme,
      minLineNumberLines: config.docs.minLineNumberLines,
      tocMaxDepth: config.docs.tocMaxDepth,
    }),
    pagefind({
      outputDirectory: "build",
      assetsDirectory: "static",
    }),
  ],
});
