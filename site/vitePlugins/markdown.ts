import { matter } from "vfile-matter";
import { unified, type Processor } from "unified";
import { VFile } from "vfile";
import { fromMarkdown } from "mdast-util-from-markdown";
import { toHast } from "mdast-util-to-hast";
import { toHtml } from "hast-util-to-html";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";
import rehypeShiki from "@shikijs/rehype";
import rehypeSlug from "rehype-slug";
import remarkGfm from "remark-gfm";
import remarkDirective from "remark-directive";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import { toc } from "mdast-util-toc";
import type { Nodes } from "mdast";
import type { Element } from "hast";
import * as config from "../src/config";
import {
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerRenderIndentGuides,
  transformerMetaHighlight,
} from "@shikijs/transformers";
import { visit } from "unist-util-visit";
import { h } from "hastscript";
import type { PluginOption } from "vite";

export default function (): PluginOption {
  return {
    name: "markdown-loader",
    async transform(code, id) {
      if (id.slice(-3) !== ".md") return;

      const file = await unified()
        .use(remarkParse)
        .use(remarkToc)
        .use(linkMigration)
        .use(remarkGfm)
        .use(remarkDirective)
        .use(styleDirectives)
        .use(remarkRehype)
        .use(rehypeShiki, {
          defaultColor: false,
          themes: {
            light: "catppuccin-latte",
            dark: "catppuccin-macchiato",
          },
          transformers: [
            transformerNotationDiff({
              matchAlgorithm: "v3",
            }),
            transformerNotationHighlight(),
            transformerRenderIndentGuides(),
            transformerMetaHighlight(),
            transformerLineNumbers({
              minLines: config.markdown.minLineNumberLines,
            }),
          ],
        })
        .use(rehypeStringify)
        .use(rehypeSlug)
        .use(rehypeAutolinkHeadings)
        .process(code);

      return `
export const content = ${JSON.stringify(String(file))};
export const frontmatter = ${JSON.stringify(file.data.matter)};
export const toc = ${JSON.stringify(file.data.toc)};`;
    },
  };
}

function remarkParse(this: Processor) {
  this.parser = (document, file) => {
    matter(file, { strip: true });
    return fromMarkdown(String(file));
  };
}
function remarkToc() {
  return (tree: Nodes, file: VFile) => {
    const { map } = toc(tree);
    if (!map) {
      file.data.toc = "";
      return;
    }
    // Remove the extranuous p element in each toc entry
    map.spread = false;
    map.children.forEach((child) => {
      child.spread = false;
    });
    file.data.toc = toHtml(toHast(map));
  };
}

// Needed according to:
// https://github.com/remarkjs/remark-directive
function styleDirectives() {
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

/**
 * Rewrites relative links in mkDocs files to point to /docs/...
 *
 * For this to work the relative link must start at the docs root
 */
function linkMigration() {
  return (tree: Nodes) => {
    visit(tree, ["link", "definition"], (node) => {
      if (node.type !== "link" && node.type !== "definition") {
        return;
      }
      // Skip external links, links pointing to /docs already and anchors
      if (!node.url || /^(https?:)?\/\/|^#/.test(node.url)) return;

      // Remove repeated leading ../  or ./
      const cleanUrl = node.url.replace(/^\.\.?|((\.\.?)\/)+|\.md$/g, "");
      if (!cleanUrl.startsWith("/")) {
        throw new Error(`invalid doc link: ${cleanUrl}`);
      }
      node.url = `${config.docs.base}/${cleanUrl}`;
    });
  };
}

function transformerLineNumbers({ minLines }: { minLines: number }) {
  return {
    pre(pre: Element) {
      const code = pre.children?.[0] as Element | undefined;
      if (!code) {
        return;
      }
      const lines = code.children.reduce((lines, node) => {
        if (node.type !== "element" || node.properties.class != "line") {
          return lines;
        }
        return lines + 1;
      }, 0);
      if (lines < minLines) {
        return;
      }
      pre.properties.class += " line-numbers";
    },
  };
}
