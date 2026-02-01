import type { Definition, Link, Root } from "mdast";
import type { Plugin } from "unified";
import * as fs from "node:fs/promises";
import path from "node:path";
import { visit } from "unist-util-visit";

class NonExistLinkError extends Error {
  override name = "NonExistLinkError";
  constructor({
    source,
    target,
    targetAbsolute,
  }: {
    source: string;
    target: string;
    targetAbsolute: string;
  }) {
    super(
      `linked to non-existent file ${target} (${targetAbsolute}) from ${source}`,
    );
  }
}
/**
 * Rewrites relative links in mkDocs files to point to /docs/...
 *
 * For this to work the relative link must start at the docs root
 */
const remarkLinkResolve: Plugin<[Record<string, `/${string}`>], Root> =
  function (replacements) {
    return async (tree, file) => {
      const nodes: (Definition | Link)[] = [];
      visit(tree, ["link", "definition"], (node) => {
        if (node.type !== "link" && node.type !== "definition") {
          return;
        }
        // Skip external or absolute links
        if (!node.url || /^\/|^(?:https?:)?\/\/|^mailto:|^#/v.test(node.url)) {
          return;
        }

        nodes.push(node);
      });
      const relative = path.relative(file.cwd, file.path);
      const results = await Promise.allSettled(
        nodes.map(async (node) => {
          const target = node.url.replace(/#.*/v, "");
          const p = path.resolve(file.cwd, relative, "..", target);
          try {
            await fs.access(p, fs.constants.R_OK);
            return {
              node,
              targetAbsolute: p,
            };
          } catch {
            throw new NonExistLinkError({
              source: file.path,
              target,
              targetAbsolute: p,
            });
          }
        }),
      );
      const rejects = results.filter((result) => result.status === "rejected");
      if (rejects.length !== 0) {
        throw new Error(
          rejects
            .map((reject) => {
              const err = reject.reason as NonExistLinkError;
              return err.message;
            })
            .join("\n"),
        );
      }
      for (const result of results) {
        if (result.status !== "fulfilled") {
          continue;
        }
        const { node, targetAbsolute } = result.value;
        const relative = path.relative(file.cwd, targetAbsolute);
        for (const dir of Object.keys(replacements)) {
          if (relative.startsWith(`${dir}/`)) {
            const url = relative.slice(dir.length + 1, -".md".length);
            node.url = `${replacements[dir]}/${url}`;
          }
        }
      }
    };
  };
export default remarkLinkResolve;
