import { defineConfig } from "vite";
import pagefind from "@clan.lol/vite-plugin-pagefind";
import * as siteConfig from "./clan-site.config.ts";
import { sveltekit } from "@sveltejs/kit/vite";
import svg from "@poppanator/sveltekit-svg";
import valuePlugin from "vite-plugin-value";

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
    pagefind({
      pluginInstance: "docs",
      siteDir: `build${siteConfig.docsBase}`,
      staticDir: "static",
      assetsDir: `build/_assets/${siteConfig.version}`,
      bundleDir: "_pagefind/docs",
      base: siteConfig.docsBase,
    }),
  ],
});
