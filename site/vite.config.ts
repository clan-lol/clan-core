import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import markdown from "./vitePlugins/markdown";

export default defineConfig({
  plugins: [sveltekit(), markdown()],
});
