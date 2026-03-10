import type { CustomMedia } from "#lib/models/viewport.ts";
import postcss from "postcss";
import postcssrc from "postcss-load-config";

export async function extractCustomMedia(): Promise<CustomMedia> {
  const { plugins } = await postcssrc();
  const out = await postcss(plugins).process(
    "@media (--medium) {}@media (--wide) {}",
    {
      from: undefined,
    },
  );
  const [medium, wide] = out.root.nodes;
  if (
    medium?.type !== "atrule" ||
    medium.name !== "media" ||
    wide?.type !== "atrule" ||
    wide.name !== "media"
  ) {
    throw new Error("Invalid custom media encountered when extracting");
  }
  return {
    medium: medium.params,
    wide: wide.params,
  };
}
