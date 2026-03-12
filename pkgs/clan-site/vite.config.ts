import { defineConfig } from "vite";
import pagefind from "@clan.lol/vite-plugin-pagefind";
import replace from "./packages/vite-plugin-replace/index.ts";
import rm from "@clan.lol/vite-plugin-rm";
import * as siteConfig from "./clan-site.config.ts";
import { sveltekit } from "@sveltejs/kit/vite";
import svg from "@poppanator/sveltekit-svg";
import valuePlugin from "vite-plugin-value";
import { versionedBase } from "#lib/models/docs/docs.server.ts";

export default defineConfig({
  server: {
    fs: {
      allow: ["./packages"],
    },
  },
  plugins: [
    sveltekit(),
    svg({
      svgoOptions: {
        plugins: ["removeXMLNS"],
      },
    }),
    valuePlugin({
      specifier: "$config",
      value: siteConfig,
    }),
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
      siteDir: "build/docs",
      staticDir: "static",
      assetsDir: `build/_assets/${siteConfig.version}`,
      bundleDir: "_pagefind/docs",
      base: versionedBase,
    }),
  ],
});
