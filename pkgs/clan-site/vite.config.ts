import { defineConfig } from "vite";
import docs2routes from "./support/vite-plugin-docs2routes.ts";
import pagefind from "@clan.lol/vite-plugin-pagefind";
import replace from "./packages/vite-plugin-replace/index.ts";
import rm from "@clan.lol/vite-plugin-rm";
import * as siteConfig from "./clan-site.config.ts";
import { sveltekit } from "@sveltejs/kit/vite";
import svg from "@poppanator/sveltekit-svg";
import value from "vite-plugin-value";
import { versionedBase } from "#lib/models/docs/docs.server.ts";

export default defineConfig({
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
    // Remove the version file from the build result. We only use this file
    // during development for the version switcher. The source exists in the
    // static folder, and is enough for the dev server to serve this file.
    // SvelteKit will copy this file to the build result but we don't really
    // need it in the build result.
    rm({
      paths: [`build/_assets/${siteConfig.version}/docs`],
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
    pagefind({
      pluginInstance: "docs",
      siteDir: "build",
      staticDir: "static",
      assetsDir: `build/_assets/${siteConfig.version}`,
      bundleDir: "_pagefind/docs",
      base: versionedBase,
    }),
  ],
});
