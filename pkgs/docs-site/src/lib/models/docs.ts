import config from "~/config";
import type {
  Markdown,
  Frontmatter as MarkdownFrontmatter,
  Heading,
} from "~/vite-plugin-markdown";

export type Path = `/${string}`;
export interface Article extends Markdown {
  path: Path;
  frontmatter: Frontmatter;
  toc: Heading[];
}
export interface Frontmatter extends MarkdownFrontmatter {
  previous?: SiblingArticle;
  next?: SiblingArticle;
}
export interface SiblingArticle {
  label: string;
  link: Path;
}
export type { Heading };

export class Docs {
  #articles: Record<Path, (() => Promise<Markdown>) | Article> = {};
  navItems: NavItem[] = [];
  async init() {
    this.#articles = Object.fromEntries(
      Object.entries(import.meta.glob<Markdown>("../../docs/**/*.md")).map(
        ([key, fn]) => {
          return [key.slice("../../docs".length, -".md".length), fn];
        },
      ),
    );

    this.navItems = await Promise.all(
      config.docs.navItems.map((navItem) => this.#normalizeNavItem(navItem)),
    );
    return this;
  }

  async getArticle(path: Path): Promise<Article | null> {
    const article = this.#articles[path];
    if (typeof article !== "function") {
      return article;
    }
    return this.#normalizeArticle(await article(), path);
  }

  async getArticles(paths: Path[]): Promise<(Article | null)[]> {
    return await Promise.all(paths.map((path) => this.getArticle(path)));
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
      };
    }

    if ("items" in navItem) {
      return {
        ...navItem,
        collapsed: !!navItem.collapsed,
        badge: normalizeBadge(navItem.badge),
        items: await Promise.all(
          navItem.items.map((navItem) => this.#normalizeNavItem(navItem)),
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
        path.startsWith(navItem.autogenerate.directory + "/"),
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
      if (titleMissing) throw new Error("Aborting due to errors.");

      articles.sort((a, b) => {
        const orderA = a.frontmatter.order;
        const orderB = b.frontmatter.order;
        if (orderA != null && orderB != null) {
          return orderA - orderB;
        }
        if (orderA != null) {
          return -1;
        }
        if (orderB != null) {
          return 1;
        }
        const titleA = a.frontmatter.title ?? a.path;
        const titleB = a.frontmatter.title ?? a.path;
        return titleA.localeCompare(titleB);
      });
      const items = await Promise.all(
        articles.map((article) =>
          this.#normalizeNavItem({
            label: article.frontmatter.title,
            link: article.path,
          }),
        ),
      );
      return {
        label:
          navItem.label ?? navItem.autogenerate.directory.split("/").at(-1),
        items,
        collapsed: !!navItem.collapsed,
        badge: normalizeBadge(navItem.badge),
      };
    }

    return {
      ...navItem,
      badge: normalizeBadge(navItem.badge),
      external: /^(https?:)?\/\//.test(navItem.link),
    };
  }

  #normalizeArticle(md: Markdown, path: Path): Article {
    let index = -1;
    const navLinks: NavLink[] = [];
    let previous: SiblingArticle | undefined;
    let next: SiblingArticle | undefined;
    visitNavItems(this.navItems, (navItem) => {
      if (!("link" in navItem)) {
        return;
      }
      if (index != -1) {
        next = {
          label: navItem.label,
          link: navItem.link,
        };
        return false;
      }
      if (navItem.link != path) {
        navLinks.push(navItem);
        return;
      }
      index = navLinks.length;
      navLinks.push(navItem);
      if (index != 0) {
        const navLink = navLinks[index - 1];
        previous = {
          label: navLink.label,
          link: navLink.link,
        };
      }
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

export function visit<T extends { children: T[] }>(
  items: T[],
  fn: (item: T, parents: T[]) => false | undefined,
): void {
  _visit(items, [], fn);
}

function _visit<T extends { children: T[] }>(
  items: T[],
  parents: T[],
  fn: (item: T, parents: T[]) => false | undefined,
): false | undefined {
  for (const item of items) {
    if (fn(item, parents) === false) {
      return false;
    }
    if (_visit(item.children, [...parents, item], fn) === false) {
      return false;
    }
  }
}

export type NavItemInput =
  | Path
  | {
      label: string;
      items: NavItemInput[];
      collapsed?: boolean;
      badge?: RawBadge;
    }
  | {
      label: string;
      autogenerate: { directory: Path };
      collapsed?: boolean;
      badge?: RawBadge;
    }
  | {
      label?: string;
      slug: Path;
      badge?: RawBadge;
    }
  | {
      label: string;
      link: Path;
      badge?: RawBadge;
    };

export type NavItem = NavGroup | NavLink;

export interface NavGroup {
  label: string;
  items: NavItem[];
  collapsed: boolean;
  badge?: Badge;
}

export interface NavLink {
  label: string;
  link: Path;
  badge?: Badge;
  external: boolean;
}

export type RawBadge = string | Badge;

export interface Badge {
  text: string;
  variant: "caution" | "normal";
}

function normalizeBadge(badge: RawBadge | undefined): Badge | undefined {
  if (!badge) {
    return undefined;
  }
  if (typeof badge === "string") {
    return {
      text: badge,
      variant: "normal",
    };
  }
  return badge;
}

function visitNavItems(
  navItems: NavItem[],
  visit: (navItem: NavItem, parents: NavItem[]) => false | undefined,
): void {
  _visitNavItems(navItems, [], visit);
}

function _visitNavItems(
  navItems: NavItem[],
  parents: NavItem[],
  visit: (heading: NavItem, parents: NavItem[]) => false | undefined,
): false | undefined {
  for (const navItem of navItems) {
    if (visit(navItem, parents) === false) {
      return false;
    }
    if ("items" in navItem) {
      if (
        _visitNavItems(navItem.items, [...parents, navItem], visit) === false
      ) {
        return false;
      }
    }
  }
}

function isPath(s: unknown): s is Path {
  return typeof s === "string" && s.startsWith("/");
}
