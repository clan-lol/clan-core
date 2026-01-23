import { VFile } from "vfile";
import type { Nodes } from "hast";
import { toString } from "hast-util-to-string";
import GithubSlugger from "github-slugger";
import { visit } from "unist-util-visit";
import { headingRank } from "hast-util-heading-rank";
import type { Heading } from ".";

const startingRank = 1;
/**
 * Adds `id`s to headings and extract out a toc
 */
export default function rehypeTocSlug({
  tocMaxDepth,
}: {
  tocMaxDepth: number;
}) {
  return (tree: Nodes, file: VFile) => {
    const slugger = new GithubSlugger();
    const toc: Heading[] = [];
    let h1Exist = false;
    const parentHeadings: Heading[] = [];
    const frontmatter = (file.data.matter || {}) as Record<string, unknown>;
    frontmatter.title = "";
    visit(tree, "element", (node) => {
      const rank = headingRank(node);
      if (!rank) return;

      let { id } = node.properties;
      if (id) {
        console.error(
          `WARNING: h${rank} has an existing id, it will be overwritten with an auto-generated one: ${file.path}`,
        );
      }
      const content = toString(node);
      id = node.properties.id = slugger.slug(content);

      if (parentHeadings.length > tocMaxDepth) {
        return;
      }
      if (rank == 1) {
        if (h1Exist) {
          console.error(
            `WARNING: only one "# title" is allowed, ignoring the rest: ${file.path}`,
          );
          return;
        }
        h1Exist = true;
        frontmatter.title = content;
      }
      const heading = { id, content, children: [] };
      const currentRank = parentHeadings.length - 1 + startingRank;
      if (rank > currentRank) {
        (parentHeadings.at(-1)?.children ?? toc).push(heading);
        parentHeadings.push(heading);
      } else if (rank == currentRank) {
        (parentHeadings.at(-2)?.children ?? toc).push(heading);
        parentHeadings.pop();
        parentHeadings.push(heading);
      } else {
        const i = rank - startingRank - 1;
        (parentHeadings?.[i].children ?? toc).push(heading);
        while (parentHeadings.length > i + 1) {
          parentHeadings.pop();
        }
        parentHeadings.push(heading);
      }
    });

    file.data.toc = toc;
  };
}
