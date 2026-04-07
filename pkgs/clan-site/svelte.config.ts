import type { Config } from "@sveltejs/kit";
import adapter from "@sveltejs/adapter-static";
import { fileURLToPath } from "node:url";
import { version } from "./clan-site.config.ts";

const DEV = process.env["MODE"] === "development";
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
