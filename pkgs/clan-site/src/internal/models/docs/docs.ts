import type { Heading, Markdown } from "@clan/vite-plugin-markdown";
import type { NavItem, NavSibling } from "./nav.ts";
import type { Path } from "$config";
import config from "$config";
import {
  findNavSiblings,
  normalizeNavItems,
  setActiveNavItems,
} from "./nav.ts";
import { mapObjectKeys } from "$lib/util.ts";

export type DocsPath = `/docs/${string}`;
export const docsBase: DocsPath = `/docs/${config.ver}`;
export const docsDir = "src/docs";

export type { Heading };

export class ArticleNotExistError extends Error {
  override name = "ArticleNotExistError";
  path: DocsPath;
  constructor(path: DocsPath) {
    super(`Document article not found, path: ${path}`);
    this.path = path;
  }
}

export interface Article {
  readonly title: string;
  readonly path: DocsPath;
  readonly content: string;
  readonly previous: NavSibling | null;
  readonly next: NavSibling | null;
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

export async function loadMarkdown(path: Path): Promise<Markdown> {
  const load = markdownLoaders[path];
  if (!load) {
    throw new ArticleNotExistError(`${docsBase}${path}`);
  }
  return await load();
}

export async function recursiveLoadMarkdowns(path: Path): Promise<Markdown[]> {
  const paths = (Object.keys(markdownLoaders) as Path[]).filter((p) =>
    p.startsWith(`${path}/`),
  );
  return await Promise.all(paths.map(async (p) => await loadMarkdown(p)));
}

export class Docs {
  readonly navItems: readonly NavItem[] = [];
  #article: Article;

  private constructor(navItems: readonly NavItem[], article: Article) {
    this.navItems = navItems;
    this.#article = article;
  }

  get article(): Article {
    return this.#article;
  }

  static async load(path: Path): Promise<Docs> {
    const navItems = await normalizeNavItems(config.docs.nav);
    const article = await loadArticle(path, navItems);
    const docs = new Docs(navItems, article);
    await docs.loadArticle(path);
    return docs;
  }

  async loadArticle(path: Path): Promise<void> {
    this.#article = await loadArticle(path, this.navItems);
  }
}

async function loadArticle(
  path: Path,
  navItems: readonly NavItem[],
): Promise<Article> {
  if (path === "/") {
    setActiveNavItems(navItems, path);
    return {
      title: config.docs.indexArticleTitle,
      content: "",
      path: docsBase,
      toc: [],
      previous: null,
      next: null,
    };
  }
  const md = await loadMarkdown(path);
  setActiveNavItems(navItems, path);
  const [previous, next] = findNavSiblings(navItems, path);

  return {
    title: md.frontmatter.title,
    content: md.content,
    path: `${docsBase}${path}`,
    toc: md.toc,
    previous,
    next,
  };
}
