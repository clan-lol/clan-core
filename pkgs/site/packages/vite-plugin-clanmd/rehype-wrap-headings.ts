import type { Plugin } from "unified";
import type { Root } from "hast";
import { headingRank } from "hast-util-heading-rank";
import { visit } from "unist-util-visit";

const rehypeWrapHeadings: Plugin<[], Root> = function () {
  return (tree) => {
    visit(tree, "element", (node) => {
      if (headingRank(node) == null) {
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
};
export default rehypeWrapHeadings;
