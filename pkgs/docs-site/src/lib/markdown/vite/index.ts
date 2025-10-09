import { unified } from "unified";
import { VFile } from "vfile";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";
import rehypeShiki from "@shikijs/rehype";
import remarkGfm from "remark-gfm";
import remarkDirective from "remark-directive";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import {
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerRenderIndentGuides,
  transformerMetaHighlight,
} from "@shikijs/transformers";
import type { PluginOption } from "vite";
import rehypeTocSlug from "./rehype-toc-slug";
import transformerLineNumbers from "./shiki-transformer-line-numbers";
import remarkParse from "./remark-parse";
import remarkAdmonition from "./remark-admonition";
import rehypeWrapHeadings from "./rehype-wrap-headings";

export type Options = {
  codeLightTheme?: string;
  codeDarkTheme?: string;
  minLineNumberLines?: number;
  tocMaxDepth?: number;
};

export default function ({
  codeLightTheme = "catppuccin-latte",
  codeDarkTheme = "catppuccin-macchiato",
  minLineNumberLines = 4,
  tocMaxDepth = 3,
}: Options = {}): PluginOption {
  return {
    name: "markdown-loader",
    async transform(code, id) {
      if (id.slice(-3) !== ".md") return;

      const file = await unified()
        .use(remarkParse)
        .use(remarkGfm)
        .use(remarkDirective)
        .use(remarkAdmonition)
        .use(remarkRehype)
        .use(rehypeTocSlug, {
          tocMaxDepth,
        })
        .use(rehypeWrapHeadings)
        .use(rehypeAutolinkHeadings)
        .use(rehypeShiki, {
          defaultColor: false,
          themes: {
            light: codeLightTheme,
            dark: codeDarkTheme,
          },
          transformers: [
            transformerNotationDiff({
              matchAlgorithm: "v3",
            }),
            transformerNotationHighlight(),
            transformerRenderIndentGuides(),
            transformerMetaHighlight(),
            transformerLineNumbers({
              minLines: minLineNumberLines,
            }),
          ],
        })
        .use(rehypeStringify)
        .process(
          new VFile({
            path: id,
            value: code,
          }),
        );

      return `
export const content = ${JSON.stringify(String(file))};
export const frontmatter = ${JSON.stringify(file.data.matter)};
export const toc = ${JSON.stringify(file.data.toc)};`;
    },
  };
}
