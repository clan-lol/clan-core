import { defineConfig } from "eslint/config";
import * as standard from "@clan.lol/coding-standard-svelte/eslint";
import svelteConfig from "./svelte.config.ts";

export default defineConfig(
  standard.base({
    gitignore: new URL(".gitignore", import.meta.url),
    svelteConfig,
  }),
  {
    files: [
      "./packages/vite-plugin-*/**/*.ts",
      "./packages/coding-standard/**/*.ts",
      "./packages/coding-standard-*/**/*.ts",
    ],
    extends: standard.node,
  },
);
