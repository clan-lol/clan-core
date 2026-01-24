import { visit } from "unist-util-visit";
import type { Nodes } from "mdast";

/**
 * Rewrites relative links in mkDocs files to point to /docs/...
 *
 * For this to work the relative link must start at the docs root
 */
export default function remarkLinkMigration() {
  return (tree: Nodes) => {
    visit(tree, ["link", "definition"], (node) => {
      if (node.type !== "link" && node.type !== "definition") {
        return;
      }
      // Skip external links, links pointing to /docs already and anchors
      if (!node.url || /^(?:https?:)?\/\/|mailto:|^#/.test(node.url)) {
        return;
      }

      // Remove repeated leading ../  or ./
      const cleanUrl = node.url.replace(/^\.\.?|(?:\.\.?\/)+|\.md$/g, "");
      if (!cleanUrl.startsWith("/")) {
        throw new Error(`invalid doc link: ${cleanUrl}`);
      }
      node.url = `/docs${cleanUrl}`;
    });
  };
}
