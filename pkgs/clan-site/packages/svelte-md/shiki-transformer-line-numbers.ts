import type { Element } from "hast";
import type { ShikiTransformer } from "shiki";

export default function transformerLineNumbers({
  minLines,
}: {
  readonly minLines: number;
}): ShikiTransformer {
  return {
    pre(pre): void {
      const code = pre.children.find(
        (child) => child.type === "element" && child.tagName === "code",
      ) as Element | undefined;
      if (!code) {
        return;
      }
      let lines = 0;
      for (const node of code.children) {
        if (node.type === "element" && node.properties.class === "line") {
          lines += 1;
        }
      }
      if (lines < minLines) {
        return;
      }
      this.addClassToHast(pre, "line-numbers");
    },
  };
}
