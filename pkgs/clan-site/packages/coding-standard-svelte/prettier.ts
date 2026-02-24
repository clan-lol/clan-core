import type { Config } from "prettier";
import svelte from "prettier-plugin-svelte";

export default {
  plugins: [svelte],
  overrides: [{ files: "*.svelte", options: { parser: "svelte" } }],
} satisfies Config;
