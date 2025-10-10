import config from "~/config";
import type {
  Markdown,
  Frontmatter as MarkdownFrontmatter,
  Heading as MarkdownHeading,
} from "./markdown";
export type Article = Markdown & {
  path: string;
  frontmatter: Frontmatter;
  toc: Heading[];
};
export type Frontmatter = MarkdownFrontmatter & {
  previous?: ArticleSibling;
  next?: ArticleSibling;
};
export type ArticleSibling = {
  label: string;
  link: string;
};
export type Heading = MarkdownHeading & {
  scrolledPast: number;
  element: Element;
  children: Heading[];
};
export class Docs {
  #allArticles: Record<string, () => Promise<Markdown>> = {};
  #loadedArticles: Record<string, Article> = {};
  navItems: NavItem[] = [];
  async init() {
    this.#allArticles = Object.fromEntries(
      Object.entries(import.meta.glob<Markdown>("../routes/docs/**/*.md")).map(
        ([key, fn]) => [key.slice("../routes/docs".length, -".md".length), fn],
      ),
    );
    this.navItems = await Promise.all(
      config.navItems.map((navItem) => this.#normalizeNavItem(navItem)),
    );
    return this;
  }

  async getArticle(path: string): Promise<Article | null> {
    const article = this.#loadedArticles[path];
    if (article) {
      return article;
    }
    const loadArticle = this.#allArticles[path];
    if (!loadArticle) {
      return null;
    }
    return this.#normalizeArticle(await loadArticle(), path);
  }

  async getArticles(paths: string[]): Promise<(Article | null)[]> {
    return await Promise.all(paths.map((path) => this.getArticle(path)));
  }

  async #normalizeNavItem(navItem: RawNavItem): Promise<NavItem> {
    if (typeof navItem === "string") {
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
      const paths = Object.keys(this.#allArticles).filter((path) =>
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

  #normalizeArticle(md: Markdown, path: string): Article {
    let index = -1;
    const navLinks: NavLink[] = [];
    let previous: ArticleSibling | undefined;
    let next: ArticleSibling | undefined;
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
      toc: normalizeHeadings(md.toc),
    };
  }
}

export function visitHeadings(
  headings: Heading[],
  visit: (heading: Heading, parents: Heading[]) => false | void,
): void {
  _visitHeadings(headings, [], visit);
}

function _visitHeadings(
  headings: Heading[],
  parents: Heading[],
  visit: (heading: Heading, parents: Heading[]) => false | void,
): false | void {
  for (const heading of headings) {
    if (visit(heading, parents) === false) {
      return false;
    }
    if (
      _visitHeadings(heading.children, [...parents, heading], visit) === false
    ) {
      return false;
    }
  }
}

export type RawNavItem =
  | string
  | {
      label: string;
      items: RawNavItem[];
      collapsed?: boolean;
      badge?: RawBadge;
    }
  | {
      label: string;
      autogenerate: { directory: string };
      collapsed?: boolean;
      badge?: RawBadge;
    }
  | {
      label?: string;
      slug: string;
      badge?: RawBadge;
    }
  | {
      label: string;
      link: string;
      badge?: RawBadge;
    };

export type NavItem = NavGroup | NavLink;

export type NavGroup = {
  label: string;
  items: NavItem[];
  collapsed: boolean;
  badge?: Badge;
};

export type NavLink = {
  label: string;
  link: string;
  badge?: Badge;
  external: boolean;
};

export type RawBadge = string | Badge;

export type Badge = {
  text: string;
  variant: "caution" | "normal";
};

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
  visit: (navItem: NavItem, parents: NavItem[]) => false | void,
): void {
  _visitNavItems(navItems, [], visit);
}

function _visitNavItems(
  navItems: NavItem[],
  parents: NavItem[],
  visit: (heading: NavItem, parents: NavItem[]) => false | void,
): false | void {
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

function normalizeHeadings(headings: MarkdownHeading[]): Heading[] {
  return headings.map((heading) => ({
    ...heading,
    scrolledPast: 0,
    children: normalizeHeadings(heading.children),
  })) as Heading[];
}
