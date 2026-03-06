import type { Plugin } from "unified";
import type { Root } from "mdast";
import { version } from "../../clan-site.config.ts";
import { visit } from "unist-util-visit";

/**
 * Add version to /docs/ links
 */
const pathBase = "/docs/";
const remarkDocsLinks: Plugin<[], Root> = function () {
  return (tree) => {
    visit(tree, ["link", "definition"] as const, (node) => {
      if (!node.url.startsWith(pathBase)) {
        return;
      }

      const path = node.url.slice(pathBase.length);
      node.url = `${pathBase}${version}${path ? `/${path}` : ""}`;
    });
  };
};
export default remarkDocsLinks;
