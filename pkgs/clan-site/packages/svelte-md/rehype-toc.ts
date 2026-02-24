import type { Plugin } from "unified";
import type { Root } from "hast";
import { headingRank } from "hast-util-heading-rank";
import { SKIP, visit } from "unist-util-visit";
import { toString } from "hast-util-to-string";

interface TocItem {
  id: string;
  content: string;
  children: TocItem[];
}

const startingRank = 1;

/**
 * Add toc and title to file.data
 */
const rehypeToc: Plugin<[{ maxTocDepth: number }], Root> = function ({
  maxTocDepth,
}) {
  return (tree, file) => {
    const toc: TocItem[] = [];
    const parentHeadings: TocItem[] = [];

    let title: string | undefined;
    visit(tree, "element", (node) => {
      const rank = headingRank(node);
      if (rank === undefined) {
        return SKIP;
      }

      const { id } = node.properties;
      if (!id) {
        throw new Error(
          `Missing id for heading level ${String(rank)}: ${file.path}`,
        );
      }

      switch (rank) {
        case 1: {
          if (title !== undefined) {
            console.error(`Multiple titles exist: ${file.path}`);
          }
          if (!title) {
            title = toString(node);
            if (!title) {
              console.error(`Empty title found: ${file.path}`);
            }
          }
          break;
        }
        default: {
          if (parentHeadings.length > maxTocDepth) {
            return SKIP;
          }

          const heading = { id, content: toString(node), children: [] };
          const contextRank = parentHeadings.length - 1 + startingRank;
          if (rank > contextRank) {
            (parentHeadings.at(-1)?.children ?? toc).push(heading);
          } else if (rank === contextRank) {
            (parentHeadings.at(-2)?.children ?? toc).push(heading);
            parentHeadings.pop();
          } else {
            const i = rank - startingRank - 1;
            (parentHeadings[i]?.children ?? toc).push(heading);
            while (parentHeadings.length > i + 1) {
              parentHeadings.pop();
            }
          }
          parentHeadings.push(heading);
        }
      }

      return;
    });
    file.data.toc = toc;
    file.data.title = title || "<Missing title>";
    // FIXME: enable this after migration
    // if (title) {
    //   file.data.title = title;
    // } else {
    //   throw new Error(`Missing title: ${file.path}`);
    // }
  };
};
export default rehypeToc;
