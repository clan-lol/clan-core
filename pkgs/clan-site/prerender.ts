import * as config from "#config";
import {
  findNavSiblings,
  getNavItems,
  getNavPointer,
} from "#lib/models/docs.server.ts";
import { prerenderDocs } from "@clan.lol/vite-plugin-docs-hmr";

await prerenderDocs({
  root: import.meta.dirname,
  srcDir: "../../docs/site",
  embedsDir: "../../docs/code-examples",
  articlesDir: "src/routes/(docs)/docs/[ver]",
  layoutDir: "src/routes/(docs)",
  render: {
    codeLightTheme: config.codeLightTheme,
    codeDarkTheme: config.codeDarkTheme,
    minLineNumberLines: config.codeMinLineNumberLines,
    maxTocDepth: config.maxTocDepth,
  },
  nav: {
    getItems: getNavItems,
    findSiblings: findNavSiblings,
    getPointer: getNavPointer,
  },
});
