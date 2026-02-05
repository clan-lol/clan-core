import type { PluginOption, ResolvedConfig } from "vite";
import pathutil from "node:path";
import pkg from "./package.json" with { type: "json" };
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeShiki from "@shikijs/rehype";
import rehypeStringify from "rehype-stringify";
import rehypeToc from "./rehype-toc.ts";
import rehypeWrapHeadings from "./rehype-wrap-headings.ts";
import remarkAdmonition from "./remark-admonition.ts";
import remarkDirective from "remark-directive";
import remarkGfm from "remark-gfm";
import remarkLinkResolve from "./remark-link-resolve.ts";
import remarkParse from "./remark-parse.ts";
import remarkRehype from "remark-rehype";
import remarkTabs from "./remark-tabs.ts";
import transformerLineNumbers from "./shiki-transformer-line-numbers.ts";
import {
  transformerMetaHighlight,
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerRenderIndentGuides,
} from "@shikijs/transformers";
import { unified } from "unified";
import { VFile } from "vfile";

export interface FrontmatterInput {
  [k: string]: unknown;
  title?: string;
}
export interface Frontmatter {
  readonly title: string;
  readonly order?: number;
}

export interface HeadingInput {
  id: string;
  content: string;
  children: HeadingInput[];
}

export interface Heading {
  readonly id: string;
  readonly content: string;
  readonly children: readonly Heading[];
}

export interface Markdown {
  readonly path: string;
  readonly relativePath: string;
  readonly content: string;
  readonly frontmatter: Frontmatter;
  readonly toc: readonly Heading[];
}

export interface Options {
  readonly codeLightTheme: string;
  readonly codeDarkTheme: string;
  readonly minLineNumberLines: number;
  readonly maxTocExtractionDepth: number;
  readonly linkResolves: Readonly<Record<string, `/${string}`>>;
}

export default function vitePluginClanmd({
  codeLightTheme,
  codeDarkTheme,
  minLineNumberLines,
  maxTocExtractionDepth,
  linkResolves,
}: Options): PluginOption {
  let config: ResolvedConfig;
  return {
    name: pkg.name,
    configResolved(resolvedConfig) {
      config = resolvedConfig;
    },

    async transform(code, path): Promise<string | undefined> {
      if (!path.endsWith(".md")) {
        return;
      }

      const file = await unified()
        .use(remarkParse)
        .use(remarkLinkResolve, linkResolves)
        .use(remarkGfm)
        .use(remarkDirective)
        .use(remarkAdmonition)
        .use(remarkTabs)
        .use(remarkRehype)
        .use(rehypeToc, {
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
            cwd: config.root,
            path,
            value: code,
          }),
        );

      const md = {
        path,
        relativePath: pathutil.relative(path, config.root),
        content: String(file),
        frontmatter: file.data.matter,
        toc: file.data.toc,
      };
      return `export default ${JSON.stringify(md)};`;
    },
  };
}
