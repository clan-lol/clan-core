import type { DocsPath, Path } from "$config";
import type { Heading, Markdown } from "@clan/vite-plugin-markdown";
import type { NavItem, NavSibling } from "./nav.ts";
import config from "$config";
import { findNavSiblings } from "./nav.ts";
import { title as indexArticleTitle } from "~/routes/(docs)/docs/[ver]/+page.svelte";
import { mapObjectKeys } from "$lib/util.ts";

export type { Heading };

export class ArticleNotExistError extends Error {
  public override name = "ArticleNotExistError";
  public path: DocsPath;
  public constructor(path: DocsPath) {
    super(`Document article not found, path: ${path}`);
    this.path = path;
  }
}

export interface Article {
  readonly title: string;
  readonly path: DocsPath;
  readonly content: string;
  readonly previous: NavSibling | undefined;
  readonly next: NavSibling | undefined;
  readonly toc: readonly Heading[];
}

const markdownLoaders = mapObjectKeys(
  import.meta.glob<Markdown>("../../../docs/**/*.md", { import: "default" }),
  ([key]) => {
    const path = key.slice("../../../docs".length, -".md".length);
    if (path === "/index") {
      return "/";
    }
    if (path.endsWith("/index")) {
      return path.slice(0, -"/index".length);
    }
    return path;
  },
);

export async function loadArticle(
  path: Path,
  navItems: readonly NavItem[],
): Promise<Article> {
  if (path === "/") {
    return {
      // FIXME: typescript-eslint can't infer types from a svelte type
      // this is probably a limitation from eslint-plugin-svelte
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      title: indexArticleTitle,
      content: "",
      path: config.docsBase,
      toc: [],
      previous: undefined,
      next: undefined,
    };
  }
  const md = await loadMarkdown(path);
  const [previous, next] = findNavSiblings(navItems, path);

  return {
    title: md.frontmatter.title,
    content: md.content,
    path: `${config.docsBase}${path}`,
    toc: md.toc,
    previous,
    next,
  };
}

export async function loadMarkdown(path: Path): Promise<Markdown> {
  const load = markdownLoaders[path];
  if (!load) {
    throw new ArticleNotExistError(`${config.docsBase}${path}`);
  }
  return await load();
}

export async function recursiveLoadMarkdowns(path: Path): Promise<Markdown[]> {
  const paths = (Object.keys(markdownLoaders) as Path[]).filter((p) =>
    p.startsWith(`${path}/`),
  );
  return await Promise.all(paths.map(async (p) => await loadMarkdown(p)));
}
