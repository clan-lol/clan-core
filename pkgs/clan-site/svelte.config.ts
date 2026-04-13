import type { Config } from "@sveltejs/kit";
import adapter from "@sveltejs/adapter-static";
import { fileURLToPath } from "node:url";
// Don't import version directly from ./clan-site.config.ts because that file
// requires some env vars to be set. This file will be imported by
// eslint.config.ts, which shouldn't require any env var to be set
import { getVersion } from "#lib/util.server.ts";

const DEV = process.env["MODE"] === "development";
const version = await getVersion();
const svelteConfig: Config = {
  kit: {
    adapter: adapter({
      pages: "build",
      assets: `build/_assets/${version}`,
      strict: true,
    }),
    paths: {
      // SvelteKit doesn't support specifying an absolute base for assets only.
      // We need that to support docs versioning via nginx. It does support a
      // full URL as the base. We will remove the https://<uuid> part in
      // vite.config.ts with the @clan.lol/vite-plugin-replace vite plugin
      assets: DEV
        ? ""
        : `https://36f875d1-c51e-47f5-83cd-3ff35490163f/_assets/${version}`,
      relative: DEV,
    },
    alias: {
      "~": fileURLToPath(new URL("src", import.meta.url)),
    },
    prerender: {
      handleUnseenRoutes(details): void {
        // We have a dev only hidden page /test
        const ignoredRoutes = new Set(["/(docs)/docs/[ver]/[test=test]"]);
        const unexpected = details.routes.filter((r) => !ignoredRoutes.has(r));
        if (unexpected.length === 0) {
          return;
        }
        throw new Error(
          `The following routes were not found while crawling the app:\n${unexpected
            .map((r) => `  - ${r}`)
            .join(
              "\n",
            )}\n\nDoc pages must be listed in the 'docsNav' config in clan-site.config.ts so that the sidebar links to them and the prerenderer can discover them.`,
        );
      },
    },
    typescript: {
      config(config) {
        config["include"] = [
          ...(config["include"] as string[]),
          "../*.ts",
          "../packages/**/*.ts",
          "../support/**/*.ts",
        ];

        config["exclude"] = [
          ...((config["exclude"] as string[] | undefined) ?? []),
          "../src/routes/(docs)/docs/[ver]/*/*",
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
      name: version,
    },
  },
};

export default svelteConfig;
