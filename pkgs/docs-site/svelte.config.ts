import adapter from "@sveltejs/adapter-static";
import type { Config } from "@sveltejs/kit";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

const config: Config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: [vitePreprocess()],
  kit: {
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
      // eslint-disable-next-line @typescript-eslint/naming-convention
      "~": new URL("src", import.meta.url).pathname,
    },
  },
  extensions: [".svelte"],
};

export default config;
