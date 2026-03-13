import type { CustomMedia } from "#lib/models/viewport.ts";
import postcss from "postcss";
import postcssrc from "postcss-load-config";
import { readFile } from "node:fs/promises";

export async function getCustomMedia(): Promise<CustomMedia> {
  const url = new URL("../../css/custom-media.css", import.meta.url);
  const src = await readFile(url, "utf8");

  // Parse CSS to extract all @custom-media names
  const names: string[] = [];
  postcss.parse(src).walkAtRules("custom-media", (node) => {
    const name = node.params.slice(0, node.params.indexOf(" "));
    names.push(name);
  });

  // Run each through postcss to get the transformed media query values
  const input = names.map((name) => `@media (${name}) {}`).join("\n");
  const { plugins } = await postcssrc();
  const out = await postcss(plugins).process(input, { from: undefined });
  function getMq(i: number): string {
    const node = out.root.nodes[i];
    if (node?.type !== "atrule" || node.name !== "media") {
      throw new Error("Invalid custom media encountered");
    }
    return node.params;
  }

  return {
    docsTablet: getMq(0),
    docsDesktop: getMq(1),
    docsTopBarFixed: getMq(2),
  };
}
