import { addClassToHast } from "shiki";
import type { ShikiTransformer } from "shiki";

export default function transformerLineNumbers({
  minLines,
}: {
  readonly minLines: number;
}): ShikiTransformer {
  return {
    pre(pre): void {
      const [code] = pre.children;
      if (!code || !("children" in code)) {
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
      addClassToHast(pre, "line-numbers");
    },
  };
}
