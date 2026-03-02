import type { Plugin } from "unified";
import type { Root } from "hast";
import { SKIP, visit } from "unist-util-visit";

const rehypeEscapeCode: Plugin<[], Root> = function () {
  return (tree) => {
    visit(tree, "text", (text, index, parent) => {
      if (!parent || index === undefined) {
        return;
      }
      if (/[{}]/.test(text.value)) {
        const value = text.value
          .replaceAll("<", "&lt;")
          .replaceAll("&", "&amp;")
          .replaceAll("{", "&#123;")
          .replaceAll("}", "&#125;");
        parent.children[index] = { type: "raw", value };
        return SKIP;
      }
      return;
    });
  };
};
export default rehypeEscapeCode;
