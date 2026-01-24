import sveltePlugin from "prettier-plugin-svelte";

const config = {
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
