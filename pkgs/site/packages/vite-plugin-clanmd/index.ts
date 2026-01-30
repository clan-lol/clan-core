import type {
  Frontmatter as FrontmatterData,
  Heading as HeadingData,
} from "./modules";
import {
  transformerMetaHighlight,
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerRenderIndentGuides,
} from "@shikijs/transformers";
import type { PluginOption } from "vite";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeShiki from "@shikijs/rehype";
import rehypeStringify from "rehype-stringify";
import rehypeTocSlug from "./rehype-toc.ts";
import rehypeWrapHeadings from "./rehype-wrap-headings.ts";
import remarkAdmonition from "./remark-admonition.ts";
import remarkDirective from "remark-directive";
import remarkGfm from "remark-gfm";
import remarkLinkMigration from "./link-migration.ts";
import remarkParse from "./remark-parse.ts";
import remarkRehype from "remark-rehype";
import remarkTabs from "./remark-tabs.ts";
import transformerLineNumbers from "./shiki-transformer-line-numbers.ts";
import { unified } from "unified";
import { VFile } from "vfile";

export interface Markdown {
  readonly content: string;
  readonly frontmatter: Frontmatter;
  readonly toc: readonly Heading[];
}

export type Frontmatter = Readonly<FrontmatterData>;

export type Heading = Readonly<Omit<HeadingData, "children">> & {
  readonly children: readonly Heading[];
};

export interface Options {
  readonly codeLightTheme: string;
  readonly codeDarkTheme: string;
  readonly minLineNumberLines: number;
  readonly maxTocExtractionDepth: number;
}

export default function vitePluginMarkdown({
  codeLightTheme,
  codeDarkTheme,
  minLineNumberLines,
  maxTocExtractionDepth,
}: Options): PluginOption {
  return {
    name: "markdown-loader",
    async transform(code, id): Promise<string | undefined> {
      if (!id.endsWith(".md")) {
        return;
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
          maxTocExtractionDepth,
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
