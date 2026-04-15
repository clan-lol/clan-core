import { defineConfig } from "vite";
import docs2routes from "./support/vite-plugin-docs2routes.ts";
import pagefind from "@clan.lol/vite-plugin-pagefind";
import replace from "./packages/vite-plugin-replace/index.ts";
import * as siteConfig from "./clan-site.config.ts";
import { sveltekit } from "@sveltejs/kit/vite";
import svg from "@poppanator/sveltekit-svg";
import value from "vite-plugin-value";
import { versionedBase } from "#lib/models/docs/docs.server.ts";
import versions from "./support/vite-plugin-versions.ts";

export default defineConfig(({ mode }) => {
  const DEV = mode === "development";
  return {
    server: {
      fs: {
        allow: ["./packages"],
      },
    },
    plugins: [
      docs2routes(),
      sveltekit(),
      svg({
        svgoOptions: {
          plugins: ["removeXMLNS"],
        },
      }),
      value({
        specifier: "$config",
        value: siteConfig,
      }),
      // Refer to kit.paths.assets in svelte.config.ts on why this is needed
      replace({
        dir: "build",
        test: /\.(?:js|html)$/,
        replacements: [
          {
            from: "https://36f875d1-c51e-47f5-83cd-3ff35490163f",
            to: "",
          },
        ],
      }),
      versions(),
      pagefind({
        pluginInstance: "docs",
        siteDir: "build",
        staticDir: "static",
        assetsDir: `build/_assets/${siteConfig.version}`,
        bundleDir: "_pagefind/docs",
        base: versionedBase,
        pagefindOptions: {
          writePlayground: DEV,
        },
      }),
    ],
  };
});
