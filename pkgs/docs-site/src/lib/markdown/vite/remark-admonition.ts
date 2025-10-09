import { visit } from "unist-util-visit";
import { h } from "hastscript";
import type { Root } from "mdast";

// Needed according to:
// https://github.com/remarkjs/remark-directive
export default function remarkAdmonition() {
  return (tree: Root) => {
    visit(tree, (node) => {
      if (
        node.type === "textDirective" ||
        node.type === "leafDirective" ||
        node.type === "containerDirective"
      ) {
        const data = (node.data ||= {});
        const hast = h(node.name, node.attributes || {});

        // Detect whether first child is a label paragraph
        const hasCustomTitle =
          node.children?.[0]?.data?.directiveLabel === true;

        // For custom title: use the existing paragraph node (will be converted to HAST)
        // For fallback: create a new paragraph with text
        const titleNode = hasCustomTitle
          ? node.children[0]
          : {
              type: "paragraph" as const,
              children: [
                {
                  type: "text" as const,
                  value: node.name,
                },
              ],
            };

        // Remove label paragraph from children if it exists
        const contentChildren = hasCustomTitle
          ? node.children.slice(1)
          : node.children;

        data.hName = "div";
        data.hProperties = {
          className: `admonition ${hast.tagName}`,
        };

        // Synthetic icon node
        const iconNode = {
          type: "text" as const,
          value: "",
          data: {
            hName: "span",
            hProperties: {
              className: ["admonition-icon"],
              "data-icon": hast.tagName,
            },
          },
        };

        // Create new children array with title wrapped in div
        // The remark-rehype plugin will convert these MDAST nodes to HAST
        node.children = [
          // Title node
          {
            type: "paragraph",
            data: {
              hName: "div",
              hProperties: { className: ["admonition-title"] },
            },
            children:
              titleNode.type === "paragraph"
                ? [iconNode, ...titleNode.children]
                : [iconNode, titleNode],
          },
          ...contentChildren,
        ];
      }
    });
  };
}
