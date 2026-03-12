import type { Plugin } from "unified";
import type { Root } from "mdast";
import { docsBase } from "../../clan-site.config.ts";
import { versionedBase } from "../../src/lib/models/docs/docs.server.ts";
import { visit } from "unist-util-visit";

/**
 * Add version to /docs/ links
 */
const remarkDocsLinks: Plugin<[], Root> = function () {
  return (tree) => {
    visit(tree, ["link", "definition"] as const, (node) => {
      if (!node.url.startsWith(`${docsBase}/`)) {
        return;
      }

      const path = node.url.slice(docsBase.length + 1);
      node.url = `${versionedBase}${path ? `/${path}` : ""}`;
    });
  };
};
export default remarkDocsLinks;
