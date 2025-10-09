import { visit } from "unist-util-visit";
import { headingRank } from "hast-util-heading-rank";
import type { Nodes } from "hast";

export default function rehypeWrapHeadings() {
  return (tree: Nodes) => {
    visit(tree, "element", (node) => {
      if (!headingRank(node)) {
        return;
      }
      node.children = [
        {
          type: "element",
          tagName: "span",
          properties: {},
          children: node.children,
        },
      ];
    });
  };
}
