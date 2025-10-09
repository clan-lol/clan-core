import type { Element } from "hast";

export default function transformerLineNumbers({
  minLines,
}: {
  minLines: number;
}) {
  return {
    pre(pre: Element) {
      const code = pre.children?.[0] as Element | undefined;
      if (!code) {
        return;
      }
      const lines = code.children.reduce((lines, node) => {
        if (node.type !== "element" || node.properties.class != "line") {
          return lines;
        }
        return lines + 1;
      }, 0);
      if (lines < minLines) {
        return;
      }
      pre.properties.class += " line-numbers";
    },
  };
}
