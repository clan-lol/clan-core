import { unified } from "unified";
import { VFile } from "vfile";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";
import rehypeShiki from "@shikijs/rehype";
import remarkGfm from "remark-gfm";
import remarkDirective from "remark-directive";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import {
  transformerMetaHighlight,
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerRenderIndentGuides,
} from "@shikijs/transformers";
import type { PluginOption } from "vite";
import rehypeTocSlug from "./rehype-toc-slug";
import transformerLineNumbers from "./shiki-transformer-line-numbers";
import remarkParse from "./remark-parse";
import remarkAdmonition from "./remark-admonition";
import remarkTabs from "./remark-tabs";
import rehypeWrapHeadings from "./rehype-wrap-headings";
import remarkLinkMigration from "./link-migration";

export interface Markdown {
  content: string;
  frontmatter: Frontmatter;
  toc: Heading[];
}

export interface Frontmatter {
  order?: number;
  title: string;
}

export interface Heading {
  id: string;
  content: string;
  children: Heading[];
}

export interface Options {
  codeLightTheme: string;
  codeDarkTheme: string;
  minLineNumberLines: number;
  tocMaxDepth: number;
}

export default function VitePluginMarkdown({
  codeLightTheme,
  codeDarkTheme,
  minLineNumberLines,
  tocMaxDepth,
}: Options): PluginOption {
  return {
    name: "markdown-loader",
    async transform(code, id) {
      if (!id.endsWith(".md")) {
        return "";
      }

      const file = await unified()
        .use(remarkParse)
        .use(remarkLinkMigration)
        .use(remarkGfm)
        .use(remarkDirective)
        .use(remarkAdmonition)
        .use(remarkTabs)
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
export const frontmatter = ${JSON.stringify(file.data["matter"])};
export const toc = ${JSON.stringify(file.data["toc"])};`;
    },
  };
}
