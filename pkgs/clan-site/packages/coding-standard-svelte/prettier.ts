import type { Config } from "prettier";

export default {
  plugins: ["prettier-plugin-svelte"],
  overrides: [{ files: "*.svelte", options: { parser: "svelte" } }],
} satisfies Config;
