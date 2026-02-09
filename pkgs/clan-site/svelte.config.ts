import type { Config } from "@sveltejs/kit";
import adapter from "@sveltejs/adapter-static";
import siteConfig from "./clan-site.config.ts";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

const DEV = process.env["MODE"] === "development";
const svelteConfig: Config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: [vitePreprocess()],
  kit: {
    // See https://svelte.dev/docs/kit/adapters for more information about adapters.
    adapter: adapter({
      pages: "build",
      assets: `build/_assets/${siteConfig.version}`,
      strict: true,
    }),
    prerender: {
      handleHttpError: "warn",
      handleMissingId: "warn",
    },
    paths: {
      // SvelteKit doesn't support specifying an absolute base for assets only,
      //  which we need to support docs versioning via nginx. It does support a
      //  full URL as the base. We will remove the https://<uuid> part in
      //  src/hooks.server.ts
      assets: DEV
        ? ""
        : `https://36f875d1-c51e-47f5-83cd-3ff35490163f/_assets/${siteConfig.version}`,
      relative: DEV,
    },
    alias: {
      "~": new URL("src", import.meta.url).pathname,
    },
    typescript: {
      config(config) {
        config["include"] = [
          ...(config["include"] as string[]),
          "../*.ts",
          "../packages/**/*.ts",
        ];
        const compOpts = config["compilerOptions"] as Record<string, unknown>;
        config["compilerOptions"] = {
          ...compOpts,
          paths: {
            ...(compOpts["paths"] as Record<string, unknown>),
            $config: ["../clan-site.config.ts"],
          },
        };
      },
    },
    version: {
      name: siteConfig.version,
    },
  },
  extensions: [".svelte"],
};

export default svelteConfig;
