import type { ShikiTransformer } from "shiki";

export default function transformerLineNumbers({
  minLines,
}: {
  minLines: number;
}): ShikiTransformer {
  return {
    pre(pre) {
      const code = pre.children?.[0];
      if (!code || !("children" in code)) {
        return;
      }
      let lines = 0;
      for (const node of code.children) {
        if (node.type === "element" && node.properties["class"] === "line") {
          lines += 1;
        }
      }
      if (lines < minLines) {
        return;
      }
      pre.properties["class"] += " line-numbers";
    },
  };
}
