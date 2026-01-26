import type {
  Heading,
  Markdown,
  Frontmatter as MarkdownFrontmatter,
} from "~/vite-plugin-markdown";
import config from "~/config";
import { visitNavItems } from "./visit";

function normalizeBadge(badge: BadgeInput | undefined): Badge | null {
  if (badge == null) {
    return null;
  }
  if (typeof badge === "string") {
    return {
      text: badge,
      variant: "normal",
    };
  }
  return badge;
}

function isPath(s: unknown): s is Path {
  return typeof s === "string" && s.startsWith("/");
}

export { visit } from "./visit";

export type Path = `/${string}`;
export interface Article extends Markdown {
  path: Path;
  frontmatter: Frontmatter;
  toc: Heading[];
}
export interface Frontmatter extends MarkdownFrontmatter {
  previous: SiblingArticle | null;
  next: SiblingArticle | null;
}
export interface SiblingArticle {
  label: string;
  link: Path;
}
export type { Heading };

export class Docs {
  #articles: Record<Path, (() => Promise<Markdown>) | Article> = {};
  navItems: NavItem[] = [];
  async init(): Promise<Docs> {
    this.#articles = Object.fromEntries(
      Object.entries(import.meta.glob<Markdown>("../../../docs/**/*.md")).map(
        ([key, fn]) => [key.slice("../../../docs".length, -".md".length), fn],
      ),
    );

    this.navItems = await Promise.all(
      config.docs.navItems.map(
        async (navItem) => await this.#normalizeNavItem(navItem),
      ),
    );
    return this;
  }

  async getArticle(path: Path): Promise<Article | null> {
    const article = this.#articles[path];
    if (!article) {
      return null;
    }

    if (typeof article !== "function") {
      return article;
    }
    return this.#normalizeArticle(await article(), path);
  }

  async getArticles(paths: Path[]): Promise<(Article | null)[]> {
    return await Promise.all(
      paths.map(async (path) => await this.getArticle(path)),
    );
  }

  async #normalizeNavItem(navItem: NavItemInput): Promise<NavItem> {
    if (isPath(navItem)) {
      const article = await this.getArticle(navItem);
      if (!article) {
        throw new Error(`Doc not found: ${navItem}`);
      }
      return {
        label: article.frontmatter.title,
        link: navItem,
        external: false,
        badge: null,
      };
    }

    if ("items" in navItem) {
      return {
        ...navItem,
        collapsed: Boolean(navItem.collapsed),
        badge: normalizeBadge(navItem.badge),
        items: await Promise.all(
          navItem.items.map(
            async (navItem) => await this.#normalizeNavItem(navItem),
          ),
        ),
      };
    }

    if ("slug" in navItem) {
      const article = await this.getArticle(navItem.slug);
      if (!article) {
        throw new Error(`Doc not found: ${navItem.slug}`);
      }
      return {
        label: navItem.label ?? article.frontmatter.title,
        link: navItem.slug,
        badge: normalizeBadge(navItem.badge),
        external: false,
      };
    }

    if ("autogenerate" in navItem) {
      const paths = (Object.keys(this.#articles) as Path[]).filter((path) =>
        path.startsWith(`${navItem.autogenerate.directory}/`),
      );
      const articles = (await this.getArticles(paths)) as Article[];

      let titleMissing = false;
      // Check frontmatter for title
      for (const article of articles) {
        if (!article.frontmatter.title) {
          console.error(`Missing # title in doc: ${article.path}`);
          titleMissing = true;
        }
      }
      if (titleMissing) {
        throw new Error("Aborting due to errors.");
      }

      articles.sort((a, b) => {
        if ("order" in a.frontmatter && "order" in b.frontmatter) {
          return a.frontmatter.order - b.frontmatter.order;
        }
        if ("order" in a.frontmatter) {
          return -1;
        }
        if ("order" in b.frontmatter) {
          return 1;
        }
        const titleA = a.frontmatter.title ?? a.path,
          titleB = a.frontmatter.title ?? a.path;
        return titleA.localeCompare(titleB);
      });
      const items = await Promise.all(
        articles.map(
          async (article) =>
            await this.#normalizeNavItem({
              label: article.frontmatter.title,
              link: article.path,
            }),
        ),
      );
      return {
        label:
          navItem.label ?? navItem.autogenerate.directory.split("/").at(-1),
        items,
        collapsed: Boolean(navItem.collapsed),
        badge: normalizeBadge(navItem.badge),
      };
    }

    return {
      ...navItem,
      badge: normalizeBadge(navItem.badge),
      external: /^(?:https?:)?\/\//.test(navItem.link),
    };
  }

  #normalizeArticle(md: Markdown, path: Path): Article {
    let index = -1;
    const navLinks: NavLink[] = [];
    let next: SiblingArticle | null = null;
    let previous: SiblingArticle | null = null;
    visitNavItems(this.navItems, (navItem) => {
      if (!("link" in navItem)) {
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
      path,
      frontmatter: {
        ...md.frontmatter,
        previous,
        next,
      },
      toc: md.toc,
    };
  }
}

export type NavItemInput =
  | Path
  | {
      label: string;
      items: NavItemInput[];
      collapsed?: boolean;
      badge?: BadgeInput;
    }
  | {
      label: string;
      autogenerate: { directory: Path };
      collapsed?: boolean;
      badge?: BadgeInput;
    }
  | {
      label?: string;
      slug: Path;
      badge?: BadgeInput;
    }
  | {
      label: string;
      link: Path;
      badge?: BadgeInput;
    };

export type NavItem = NavGroup | NavLink;

export interface NavGroup {
  label: string;
  items: NavItem[];
  collapsed: boolean;
  badge: Badge | null;
}

export interface NavLink {
  label: string;
  link: Path;
  badge: Badge | null;
  external: boolean;
}

export type BadgeInput = string | Badge;

export interface Badge {
  text: string;
  variant: "caution" | "normal";
}
