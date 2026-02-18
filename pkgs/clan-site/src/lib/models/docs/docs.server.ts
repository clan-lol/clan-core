import type { Article } from "./docs.ts";
import type { DocsPath, Path } from "$config";
import type { Markdown } from "@clan/vite-plugin-markdown";
import type { NavItem } from "./nav.ts";
import config from "$config";
import { findNavSiblings, getNavPath } from "./nav.server.ts";
import { title as indexArticleTitle } from "~/routes/(docs)/docs/[ver]/+page.svelte";
import { mapObjectKeys } from "$lib/util.ts";

export class ArticleNotExistError extends Error {
  public override name = "ArticleNotExistError";
  public path: DocsPath;
  public constructor(path: DocsPath) {
    super(`Article not found: ${path}`);
    this.path = path;
  }
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
// eslint-disable-next-line @typescript-eslint/require-await
markdownLoaders["/"] = async (): Promise<Markdown> => ({
  frontmatter: {
    title: indexArticleTitle,
  },
  content: "",
  toc: [],
  path: "/",
  relativePath: ".",
});

export async function loadArticle(
  path: Path,
  navItems: readonly NavItem[],
): Promise<Article> {
  const md = await loadMarkdown(path);
  const navPath = getNavPath(navItems, path);
  const [previous, next] = findNavSiblings(navItems, path);

  return {
    title: md.frontmatter.title,
    content: md.content,
    path: `${config.docsBase}${path}`,
    previous,
    next,
    navPath,
    toc: md.toc,
  };
}

export async function loadMarkdown(path: Path): Promise<Markdown> {
  const load = markdownLoaders[path];
  if (!load) {
    throw new ArticleNotExistError(`${config.docsBase}${path}`);
  }
  return await load();
}

export async function recursiveLoadMarkdowns(
  pathPrefix: Path,
): Promise<Markdown[]> {
  const paths = (Object.keys(markdownLoaders) as Path[]).filter((p) =>
    p.startsWith(`${pathPrefix}/`),
  );
  return await Promise.all(paths.map(async (p) => await loadMarkdown(p)));
}
