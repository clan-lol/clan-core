import type { CustomMedia } from "./custom-media.ts";
import postcss from "postcss";
import postcssrc from "postcss-load-config";

export async function extractCustomMedia(): Promise<CustomMedia> {
  const { plugins } = await postcssrc();
  const out = await postcss(plugins).process("@media (--wide) {}", {
    from: undefined,
  });
  const [node] = out.root.nodes;
  if (node?.type !== "atrule" || node.name !== "media") {
    throw new Error("Invalid custom media encountered when extracting");
  }
  return {
    wide: node.params,
  };
}
