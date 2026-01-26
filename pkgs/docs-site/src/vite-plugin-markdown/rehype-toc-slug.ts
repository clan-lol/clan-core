import GithubSlugger from "github-slugger";
import type { Heading } from ".";
import { headingRank } from "hast-util-heading-rank";
import type { Plugin } from "unified";
import type { Root } from "hast";
import { toString } from "hast-util-to-string";
import { visit } from "unist-util-visit";

const startingRank = 1;

/**
 * Adds `id`s to headings and extract out a toc
 */
const rehypeTocSlug: Plugin<[{ tocMaxDepth: number }], Root> = function ({
  tocMaxDepth,
}) {
  return (tree, file) => {
    const slugger = new GithubSlugger();
    const toc: Heading[] = [];
    let h1Exist = false;
    const parentHeadings: Heading[] = [];
    const frontmatter = file.data.matter;
    if (!frontmatter) {
      throw new Error("frontmatter not found");
    }
    frontmatter["title"] = "";
    visit(tree, "element", (node) => {
      const rank = headingRank(node);
      if (rank == null) {
        return;
      }

      let { id } = node.properties;
      if (id == null) {
        console.error(
          `WARNING: h${rank} has an existing id, it will be overwritten with an auto-generated one: ${file.path}`,
        );
      }
      const content = toString(node);
      id = slugger.slug(content);
      node.properties["id"] = id;

      if (parentHeadings.length > tocMaxDepth) {
        return;
      }
      if (rank === 1) {
        if (h1Exist) {
          console.error(
            `WARNING: only one "# title" is allowed, ignoring the rest: ${file.path}`,
          );
          return;
        }
        h1Exist = true;
        frontmatter["title"] = content;
      }
      const heading = { id, content, children: [] };
      const currentRank = parentHeadings.length - 1 + startingRank;
      if (rank > currentRank) {
        (parentHeadings.at(-1)?.children ?? toc).push(heading);
      } else if (rank === currentRank) {
        (parentHeadings.at(-2)?.children ?? toc).push(heading);
        parentHeadings.pop();
      } else {
        const i = rank - startingRank - 1;
        (parentHeadings?.[i]?.children ?? toc).push(heading);
        while (parentHeadings.length > i + 1) {
          parentHeadings.pop();
        }
      }
      parentHeadings.push(heading);
    });

    file.data["toc"] = toc;
  };
};
export default rehypeTocSlug;
