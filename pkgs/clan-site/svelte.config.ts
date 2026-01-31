import type { Config } from "@sveltejs/kit";
import adapter from "@sveltejs/adapter-static";
import siteConfig from "./clan-site.config.ts";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

const svelteConfig: Config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: [vitePreprocess()],
  kit: {
    // See https://svelte.dev/docs/kit/adapters for more information about adapters.
    adapter: adapter({
      pages: "build",
      assets: `build/_assets/${siteConfig.ver}`,
      strict: true,
    }),
    prerender: {
      handleHttpError: "warn",
      handleMissingId: "warn",
    },
    alias: {
      // eslint-disable-next-line @typescript-eslint/naming-convention
      "~": new URL("src", import.meta.url).pathname,
      $internal: new URL("src/internal", import.meta.url).pathname,
    },
    version: {
      name: siteConfig.ver,
    },
  },
  extensions: [".svelte"],
};

export default svelteConfig;
