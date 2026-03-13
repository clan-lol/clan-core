import { defineConfig } from "vite";
import docsHmr from "@clan.lol/vite-plugin-docs-hmr";
import {
  findNavSiblings,
  getNavItems,
  getNavPointer,
} from "#lib/models/docs.server.ts";
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
    docsHmr({
      srcDir: "../../docs/site",
      embedsDir: "../../docs/code-examples",
      articlesDir: "src/routes/(docs)/docs/[ver]",
      layoutDir: "src/routes/(docs)",
      render: {
        codeLightTheme: siteConfig.codeLightTheme,
        codeDarkTheme: siteConfig.codeDarkTheme,
        minLineNumberLines: siteConfig.codeMinLineNumberLines,
        maxTocDepth: siteConfig.maxTocDepth,
      },
      nav: {
        getItems: getNavItems,
        findSiblings: findNavSiblings,
        getPointer: getNavPointer,
      },
    }),
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
