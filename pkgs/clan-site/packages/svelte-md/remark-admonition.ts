import type { Plugin } from "unified";
import type { Root } from "mdast";
import { visit } from "unist-util-visit";

const defaultType = "note";
const types = ["note", "important", "danger", "tip"] as const;

export type AdmonitionType = (typeof types)[number];

const typeSet = new Set<string>(types);
const remarkAdmonition: Plugin<[], Root> = function () {
  return (tree, file) => {
    visit(tree, (node) => {
      if (node.type !== "containerDirective" || node.name !== "admonition") {
        return;
      }
      let type = node.attributes?.["type"];
      if (typeof type === "string") {
        if (!type) {
          type = defaultType;
        } else if (!typeSet.has(type)) {
          console.warn(`Invalid admonition type "${type}": ${file.path}`);
          type = defaultType;
        }
      } else {
        type = defaultType;
      }
      let title = "";
      const [titleNode] = node.children;
      if (
        titleNode?.type === "paragraph" &&
        titleNode.data?.directiveLabel === true
      ) {
        const [text] = titleNode.children;
        if (text?.type === "text") {
          title = text.value;
        } else {
          console.warn(
            `Invalid AST generated for admonition directive's title: ${file.path}`,
          );
        }
        node.children.shift();
      }

      const collapsed = node.attributes
        ? "collapsed" in node.attributes
        : false;

      node.children = [
        {
          type: "html",
          value: `<Admonition type={${JSON.stringify(type)}}${title ? ` title=${JSON.stringify(type)}` : ""}${collapsed ? " collapsed" : ""}>`,
        },
        ...node.children,
        {
          type: "html",
          value: `</Admonition>`,
        },
      ];

      file.data.svelteComponents ??= new Set();
      file.data.svelteComponents.add("Admonition");
    });
  };
};
export default remarkAdmonition;
