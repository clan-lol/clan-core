import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import { matter } from "vfile-matter";
import { unified } from "unified";
import { VFile } from "vfile";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";
import rehypeShiki from "@shikijs/rehype";
import rehypeSlug from "rehype-slug";
import remarkGfm from "remark-gfm";
import remarkDirective from "remark-directive";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import { toc } from "mdast-util-toc";
import type { Nodes } from "mdast";
import {
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerRenderIndentGuides,
  transformerMetaHighlight,
} from "@shikijs/transformers";
import { visit } from "unist-util-visit";
import { h } from "hastscript";

// Needed according to:
// https://github.com/remarkjs/remark-directive
export function styleDirectives() {
  /**
   * @param {Root} tree
   *   Tree.
   * @returns {undefined}
   *   Nothing.
   */
  return (tree: Nodes) => {
    visit(tree, (node) => {
      if (
        node.type === "textDirective" ||
        node.type === "leafDirective" ||
        node.type === "containerDirective"
      ) {
        const data = (node.data ||= {});
        const hast = h(node.name, node.attributes);

        // Detect whether first child is a label paragraph
        const hasCustomTitle =
          node.children?.[0]?.data?.directiveLabel === true;

        // For custom title: use the existing paragraph node (will be converted to HAST)
        // For fallback: create a new paragraph with text
        const titleNode = hasCustomTitle
          ? node.children[0]
          : {
              type: "paragraph" as const,
              children: [
                {
                  type: "text" as const,
                  value: node.name,
                },
              ],
            };

        // Remove label paragraph from children if it exists
        const contentChildren = hasCustomTitle
          ? node.children.slice(1)
          : node.children;

        data.hName = "div";
        data.hProperties = {
          className: `admonition ${hast.tagName}`,
        };

        // Synthetic icon node
        const iconNode = {
          type: "text" as const,
          value: "",
          data: {
            hName: "span",
            hProperties: {
              className: ["admonition-icon"],
              "data-icon": hast.tagName,
            },
          },
        };

        // Create new children array with title wrapped in div
        // The remark-rehype plugin will convert these MDAST nodes to HAST
        node.children = [
          // Title node
          {
            type: "paragraph" as const,
            data: {
              hName: "div",
              hProperties: { className: ["admonition-title"] },
            },
            children:
              titleNode.type === "paragraph"
                ? [iconNode, ...titleNode.children]
                : [iconNode, titleNode],
          },
          ...contentChildren,
        ];
      }
    });
  };
}

export default defineConfig({
  plugins: [
    sveltekit(),
    {
      name: "markdown-loader",
      async transform(code, id) {
        if (id.slice(-3) !== ".md") return;

        // TODO: move VFile into unified
        const file = new VFile(code);
        matter(file, { strip: true });
        const html = await unified()
          .use(remarkParse)
          .use(remarkGfm)
          .use(remarkDirective)
          .use(styleDirectives)
          .use(remarkRehype)
          .use(rehypeShiki, {
            themes: {
              light: "vitesse-light",
              dark: "vitesse-dark",
            },
            transformers: [
              transformerNotationDiff({
                matchAlgorithm: "v3",
              }),
              transformerNotationHighlight(),
              transformerRenderIndentGuides(),
              transformerMetaHighlight(),
            ],
          })
          .use(rehypeStringify)
          .use(rehypeSlug)
          .use(rehypeAutolinkHeadings)
          .process(String(code));

        const parsed = await unified()
          .use(remarkParse)
          .use(() => (tree) => {
            const result = toc(tree as Nodes);
            return result.map;
          })
          .use(remarkRehype)
          .use(rehypeStringify)
          .process(file);

        return `
export const content = ${JSON.stringify(String(html))};
export const frontmatter = ${JSON.stringify(file.data.matter)};
export const toc = ${JSON.stringify(String(parsed))};`;
      },
    },
  ],
});
