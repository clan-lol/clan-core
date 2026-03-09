import type { TocItems } from "./rehype-toc.ts";
import { matter } from "vfile-matter";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeEscape from "./rehype-escape.ts";
import rehypeMermaid from "rehype-mermaid";
import rehypeShiki from "@shikijs/rehype";
import rehypeSlug from "rehype-slug";
import rehypeStringify from "rehype-stringify";
import rehypeToc from "./rehype-toc.ts";
import remarkAdmonition from "./remark-admonition.ts";
import remarkCodeEmbed from "./remark-code-embed.ts";
import remarkDirective from "remark-directive";
import remarkDisableTextDirective from "./remark-disable-text-directive.ts";
import remarkDocsLinks from "./remark-docs-links.ts";
import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import remarkTabs from "./remark-tabs.ts";
import transformerCustom from "./shiki-transformer-custom.ts";
import {
  transformerMetaHighlight,
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerRenderIndentGuides,
} from "@shikijs/transformers";
import { unified } from "unified";
import { VFile } from "vfile";

export interface Options {
  readonly root: string;
  readonly filename: string;
  readonly codeLightTheme: string;
  readonly codeDarkTheme: string;
  readonly minLineNumberLines: number;
  readonly maxTocDepth: number;
  readonly codeEmbedDir: string;
  readonly componentsSpecifierPrefix: string;
}

export type { AdmonitionType } from "./remark-admonition.ts";
export type { TocItem } from "./rehype-toc.ts";
export type { TocItems };

export type Frontmatter = Readonly<Record<string, unknown>>;

export interface Output {
  readonly title: string;
  readonly frontmatter: Frontmatter;
  readonly svelteComponents: Set<string>;
  readonly markup: string;
  readonly toc: TocItems;
}

export async function render(source: string, opts: Options): Promise<Output> {
  const data = {
    svelteComponents: new Set<string>(),
    title: "",
    toc: [],
    frontmatter: {},
  };
  const file = new VFile({
    cwd: opts.root,
    path: opts.filename,
    value: source,
    data,
  });
  matter(file, { strip: true });
  await unified()
    .use(remarkParse)
    .use(remarkDocsLinks)
    .use(remarkGfm)
    .use(remarkDirective)
    .use(remarkDisableTextDirective)
    .use(remarkAdmonition)
    .use(remarkTabs)
    .use(remarkCodeEmbed, {
      dir: opts.codeEmbedDir,
    })
    .use(remarkRehype, {
      allowDangerousHtml: true,
    })
    .use(rehypeSlug)
    .use(rehypeToc, {
      maxTocDepth: opts.maxTocDepth,
    })
    .use(rehypeAutolinkHeadings, {
      behavior: "append",
      properties: {
        ariaHidden: "true",
        tabIndex: -1,
        "data-pagefind-ignore": "true",
      },
      content: {
        type: "text",
        value: "🔗",
      },
      test(node) {
        return node.tagName !== "h1";
      },
    })
    .use(rehypeMermaid, {
      strategy: "img-svg",
    })
    .use(rehypeShiki, {
      defaultColor: false,
      defaultLanguage: "text",
      tabindex: false,
      themes: {
        light: opts.codeLightTheme,
        dark: opts.codeDarkTheme,
      },
      transformers: [
        transformerNotationDiff({
          matchAlgorithm: "v3",
        }),
        transformerNotationHighlight(),
        transformerRenderIndentGuides(),
        transformerMetaHighlight(),
        transformerCustom({
          minLines: opts.minLineNumberLines,
        }),
      ],
    })
    .use(rehypeEscape)
    .use(rehypeStringify, {
      allowDangerousHtml: true,
    })
    .process(file);
  return {
    svelteComponents: data.svelteComponents,
    title: data.title,
    markup: String(file),
    frontmatter: data.frontmatter,
    toc: data.toc,
  };
}
