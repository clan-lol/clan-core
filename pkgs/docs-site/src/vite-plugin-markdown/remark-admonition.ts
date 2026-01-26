import type { ContainerDirectiveData } from "mdast-util-directive";
import { isDirectiveParagraph } from "./util";
import type { Plugin } from "unified";
import type { Root } from "mdast";
import { visit } from "unist-util-visit";

const names = new Set(["note", "important", "danger", "tip"]);

// Adapted from https://github.com/remarkjs/remark-directive
const remarkAdmonition: Plugin<[], Root> = function () {
  return (tree) => {
    visit(tree, (node) => {
      if (node.type !== "containerDirective" || !names.has(node.name)) {
        return;
      }

      const data: ContainerDirectiveData = {};
      node.data ??= data;
      data.hName = "div";
      data.hProperties = {
        className: `md-admonition is-${node.name}`,
      };
      let title: string;
      const p = node.children?.[0];
      if (isDirectiveParagraph(p) && p.children?.[0]?.type === "text") {
        node.children.shift();
        title = p.children[0].value;
      } else {
        title = node.name;
      }

      node.children = [
        {
          type: "paragraph",
          data: {
            hName: "div",
            hProperties: { className: ["md-admonition-title"] },
          },
          children: [
            {
              type: "text",
              data: {
                hName: "span",
                hProperties: { className: ["md-admonition-icon"] },
              },
              value: "",
            },
            {
              type: "text",
              value: title,
            },
          ],
        },
        ...node.children,
      ];
    });
  };
};
export default remarkAdmonition;
