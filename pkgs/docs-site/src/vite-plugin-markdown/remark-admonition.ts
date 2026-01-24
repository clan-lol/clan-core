import { visit } from "unist-util-visit";
import type { Paragraph, Root, Text } from "mdast";
import type { ContainerDirectiveData } from "mdast-util-directive";

const names = ["note", "important", "danger", "tip"];

// Adapted from https://github.com/remarkjs/remark-directive
export default function remarkAdmonition() {
  return (tree: Root) => {
    visit(tree, (node) => {
      if (node.type !== "containerDirective" || !names.includes(node.name)) {
        return;
      }

      const data: ContainerDirectiveData = {};
      node.data ||= data;
      data.hName = "div";
      data.hProperties = {
        className: `md-admonition is-${node.name}`,
      };
      let title: string;
      if (node.children?.[0]?.data?.directiveLabel) {
        const p = node.children.shift() as Paragraph;
        title = (p.children[0] as Text).value;
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
}
