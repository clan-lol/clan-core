import type { Plugin } from "unified";
import type { Root } from "mdast";
import { visit } from "unist-util-visit";

// Based on
// https://github.com/remarkjs/remark-directive/issues/19#issuecomment-2736671715
const remarkDisableTextDirective: Plugin<[], Root> = function () {
  return (tree) => {
    visit(tree, "textDirective", (directive, index, parent) => {
      if (!parent || index === undefined) {
        return;
      }
      parent.children[index] = { type: "text", value: `:${directive.name}` };
    });
  };
};
export default remarkDisableTextDirective;
