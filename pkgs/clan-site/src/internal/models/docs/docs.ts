import type {
  Heading,
  Markdown,
  Frontmatter as MarkdownFrontmatter,
} from "vite-plugin-clanmd";
import type { NavItem, NavLink } from "./nav.ts";
import type { Path } from "$config";
import config from "$config";
import { normalizeNavItem } from "./nav.ts";
import { visit } from "$lib/util.ts";

export const docsBase: `/docs/${string}` = `/docs/${config.ver}`;

export type { Heading };

export type DocsPath = `/docs/${string}`;

export class ArticleNotExistError extends Error {
  override name = "ArticleNotExistError";
  path: DocsPath;
  constructor(path: DocsPath) {
    super(`Document article not found, path: ${path}`);
    this.path = path;
  }
}

export interface Article extends Markdown {
  readonly path: DocsPath;
  readonly frontmatter: Frontmatter;
  readonly toc: readonly Heading[];
}
export interface Frontmatter extends MarkdownFrontmatter {
  order?: number;
  previous: SiblingArticle | null;
  next: SiblingArticle | null;
}
export interface SiblingArticle {
  label: string;
  link: DocsPath;
}

export class Docs {
  navItems: readonly NavItem[] = [];
  #articles: Record<Path, (() => Promise<Markdown>) | Article> = {};
  async init(): Promise<Docs> {
    this.#articles = Object.fromEntries(
      Object.entries(import.meta.glob<Markdown>("../../../docs/**/*.md")).map(
        ([key, fn]) => {
          const path = key.slice("../../../docs".length, -".md".length);
          if (path === "/index") {
            return ["/", fn];
          }
          return [path, fn];
        },
      ),
    );

    this.navItems = await Promise.all(
      config.docs.nav.map(
        async (navItem) => await normalizeNavItem(this, navItem),
      ),
    );
    return this;
  }

  async loadArticle(path: Path): Promise<Article> {
    const article = this.#articles[path];
    if (!article) {
      throw new ArticleNotExistError(`${docsBase}${path}`);
    }

    if (typeof article !== "function") {
      return article;
    }
    return this.#loadArticle(await article(), path);
  }

  async loadAutoGenArticle(autoGenPath: Path): Promise<Article[]> {
    const paths = (Object.keys(this.#articles) as Path[]).filter((path) =>
      path.startsWith(`${autoGenPath}/`),
    );
    return await Promise.all(
      paths.map(async (path) => await this.loadArticle(path)),
    );
  }

  #loadArticle(md: Markdown, path: Path): Article {
    let index = -1;
    const navLinks: NavLink[] = [];
    let next: SiblingArticle | null = null;
    let previous: SiblingArticle | null = null;
    visit(this.navItems, "items", (navItem) => {
      if (!("link" in navItem) || navItem.external) {
        return;
      }
      if (index !== -1) {
        next = {
          label: navItem.label,
          link: navItem.link,
        };
        return "break";
      }
      if (navItem.link !== path) {
        navLinks.push(navItem);
        return;
      }
      index = navLinks.length;
      navLinks.push(navItem);
      const navLink = navLinks[index - 1];
      if (navLink) {
        previous = {
          label: navLink.label,
          link: navLink.link,
        };
      }
      return;
    });
    return {
      ...md,
      path: `${docsBase}${path}`,
      frontmatter: {
        ...md.frontmatter,
        previous,
        next,
      },
      toc: md.toc,
    };
  }
}
