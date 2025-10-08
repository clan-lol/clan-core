import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import markdown from "./src/lib/markdown/vite";

export default defineConfig({
  plugins: [sveltekit(), markdown()],
});
