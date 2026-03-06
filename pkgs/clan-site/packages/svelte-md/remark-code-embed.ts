import type { Code, Root } from "mdast";
import type { Plugin } from "unified";
import pathutil from "node:path";
import { readFile } from "node:fs/promises";
import { visit } from "unist-util-visit";

/**
 * Embed files in code blocks with ```lang embed=path
 */
const remarkCodeEmbed: Plugin<[{ dir: string }], Root> = function ({ dir }) {
  return async (tree) => {
    const embeds: { node: Code; path: string }[] = [];
    visit(tree, "code", (node) => {
      if (!node.meta) {
        return;
      }
      const result = /\bembed=(?:(?<rawPath>\S+)|"(?<strPath>[^"]+)")/.exec(
        node.meta,
      );
      if (!result?.groups) {
        return;
      }
      const path = result.groups["rawPath"] || result.groups["strPath"];
      if (!path) {
        return;
      }
      node.meta =
        node.meta.slice(0, result.index) +
        node.meta.slice(result.index + result[0].length);
      embeds.push({ node, path: pathutil.join(dir, path) });
    });

    await Promise.all(
      embeds.map(async ({ node, path }) => {
        node.value = await readFile(path, { encoding: "utf8" });
      }),
    );
  };
};
export default remarkCodeEmbed;
