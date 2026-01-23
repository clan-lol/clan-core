import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";
import { type Config } from "@sveltejs/kit";

const config: Config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: [vitePreprocess()],
  kit: {
    // adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
    // If your environment is not supported, or you settled on a specific environment, switch out the adapter.
    // See https://svelte.dev/docs/kit/adapters for more information about adapters.
    adapter: adapter({
      pages: "build",
      strict: true,
    }),
    prerender: {
      handleHttpError: "warn",
      handleMissingId: "warn",
    },
    alias: {
      "~": new URL("src", import.meta.url).pathname,
    },
  },
  extensions: [".svelte"],
};

export default config;
