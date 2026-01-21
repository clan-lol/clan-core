import { type Config } from "prettier";
import sveltePlugin from "prettier-plugin-svelte";

const config: Config = {
  plugins: [sveltePlugin],
  overrides: [
    {
      files: "*.svelte",
      options: {
        parser: "svelte",
      },
    },
  ],
};
export default config;
