import type { Plugin } from "unified";
import type { Root } from "mdast";
import { visit } from "unist-util-visit";

/**
 * Rewrites relative links in mkDocs files to point to /docs/...
 *
 * For this to work the relative link must start at the docs root
 */
const remarkLinkMigration: Plugin<[], Root> = function () {
  return (tree) => {
    visit(tree, ["link", "definition"], (node) => {
      if (node.type !== "link" && node.type !== "definition") {
        return;
      }
      // Skip external links, links pointing to /docs already and anchors
      if (!node.url || /^(?:https?:)?\/\/|mailto:|^#/.test(node.url)) {
        return;
      }

      // Remove repeated leading ../  or ./
      const cleanUrl = node.url.replaceAll(/^\.\.?|^(?:\.\.?\/)+|\.md$/g, "");
      if (!cleanUrl.startsWith("/")) {
        throw new Error(`invalid doc link: ${cleanUrl}`);
      }
      node.url = `/docs${cleanUrl}`;
    });
  };
};
export default remarkLinkMigration;
