import type { Plugin } from "unified";
import type { Root } from "mdast";
import { SKIP, visit } from "unist-util-visit";

const remarkTabs: Plugin<[], Root> = function () {
  return (tree, file) => {
    // Type casting is necessary because of typescript limitation
    // https://typescript-eslint.io/rules/no-unnecessary-condition/#values-modified-within-function-calls
    let foundTabs = false as boolean;
    visit(tree, "containerDirective", (node, index, parent) => {
      if (!parent || index === undefined || node.name !== "tabs") {
        return;
      }
      foundTabs = true;

      let foundTab = false as boolean;
      visit(node, "containerDirective", (node, index, parent) => {
        if (!parent || index === undefined || node.name !== "tab") {
          return;
        }
        foundTab = true;

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
              `Invalid AST generated for tab directive's title: ${file.path}`,
            );
          }
          node.children.shift();
        }
        parent.children.splice(
          index,
          1,
          {
            type: "html",
            value: `<Tab title=${JSON.stringify(title)}>`,
          } as const,
          ...node.children,
          {
            type: "html",
            value: `</Tab>`,
          } as const,
        );
        return;
      });

      if (!foundTab) {
        throw new Error(
          `A tabs directive must contain at least one tab directive: ${file.path}`,
        );
      }

      parent.children.splice(
        index,
        1,
        {
          type: "html",
          value: `<Tabs>`,
        } as const,
        ...node.children,
        {
          type: "html",
          value: `</Tabs>`,
        } as const,
      );

      return SKIP;
    });
    if (foundTabs) {
      file.data.svelteComponents ??= new Set();
      file.data.svelteComponents.add("Tabs");
      file.data.svelteComponents.add("Tab");
    }
  };
};
export default remarkTabs;
