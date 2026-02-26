import type { Plugin } from "unified";
import type { Root } from "hast";
import { headingRank } from "hast-util-heading-rank";
import { SKIP, visit } from "unist-util-visit";
import { toString } from "hast-util-to-string";

export interface TocItem {
  readonly id: string;
  readonly rank: number;
  readonly label: string;
  readonly children: TocItems;
}
export type TocItems = readonly TocItem[];

// We skip putting h1 to toc, so all other headings are considered to be nested
// under h1, which mean the starting context rank is 1
const startingContextRank = 1;

/**
 * Add toc and title to file.data
 */
const rehypeToc: Plugin<[{ maxTocDepth: number }], Root> = function ({
  maxTocDepth,
}) {
  return (tree, file) => {
    const toc: TocItem[] = [];
    let parentHeadings: TocItem[] = [];

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
          if (title) {
            console.error(`Multiple titles exist: ${file.path}`);
          } else {
            title = toString(node);
            if (!title) {
              console.error(`Empty title found: ${file.path}`);
            }
          }
          break;
        }
        default: {
          const heading = { id, rank, label: toString(node), children: [] };
          const contextRank =
            parentHeadings.at(-1)?.rank ?? startingContextRank;
          let siblings: TocItem[];
          if (rank > contextRank && parentHeadings.length < maxTocDepth) {
            siblings =
              (parentHeadings.at(-1)?.children as TocItem[] | undefined) ?? toc;
            siblings.push(heading);
            parentHeadings.push(heading);
          } else if (rank === contextRank) {
            parentHeadings.pop();
            siblings =
              (parentHeadings.at(-1)?.children as TocItem[] | undefined) ?? toc;
            siblings.push(heading);
            parentHeadings.push(heading);
          } else {
            const i = parentHeadings.findIndex(
              (parentHeading) => parentHeading.rank < rank,
            );
            const parentHeading = parentHeadings[i];
            if (parentHeading) {
              siblings = parentHeading.children as TocItem[];
              parentHeadings = parentHeadings.slice(0, i + 1);
            } else {
              siblings = toc;
              parentHeadings = [];
            }
            siblings.push(heading);
            parentHeadings.push(heading);
          }
        }
      }

      return;
    });
    file.data.toc = toc as TocItems;
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
