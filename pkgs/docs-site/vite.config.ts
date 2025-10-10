import { sveltekit } from "@sveltejs/kit/vite";
import { pagefind } from "vite-plugin-pagefind";
import { defineConfig } from "vite";
import markdown from "./src/lib/markdown/vite";

export default defineConfig({
  plugins: [
    sveltekit(),
    markdown(),
    pagefind({
      outputDirectory: "build",
      assetsDirectory: "static",
    }),
  ],
});
