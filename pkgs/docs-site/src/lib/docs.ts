import config from "~/config";
import type { Markdown, Heading as MarkdownHeading } from "./markdown";
export type Article = Markdown & {
  toc: Heading[];
};
export type Heading = MarkdownHeading & {
  scrolledPast: number;
  element: Element;
  children: Heading[];
};
export class Docs {
  #allArticles: Record<string, () => Promise<Markdown>> = {};
  #loadedArticles: Record<string, Article> = {};
  navLinks: NavLink[] = [];
  async init() {
    this.#allArticles = Object.fromEntries(
      Object.entries(import.meta.glob<Markdown>("../routes/docs/**/*.md")).map(
        ([key, fn]) => [key.slice("../routes/docs".length, -".md".length), fn],
      ),
    );
    this.navLinks = await Promise.all(
      config.navLinks.map((navLink) => this.#normalizeNavLink(navLink)),
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
    const loaded = await loadArticle();
    return {
      ...loaded,
      toc: normalizeHeadings(loaded.toc),
    };
  }

  async getArticles(paths: string[]): Promise<(Article | null)[]> {
    return await Promise.all(paths.map((path) => this.getArticle(path)));
  }

  async #normalizeNavLink(navLink: RawNavLink): Promise<NavLink> {
    if (typeof navLink === "string") {
      const article = await this.getArticle(navLink);
      if (!article) {
        throw new Error(`Doc not found: ${navLink}`);
      }
      return {
        label: article.frontmatter.title,
        link: navLink,
        external: false,
      };
    }

    if ("items" in navLink) {
      return {
        ...navLink,
        collapsed: !!navLink.collapsed,
        badge: normalizeBadge(navLink.badge),
        items: await Promise.all(
          navLink.items.map((navLink) => this.#normalizeNavLink(navLink)),
        ),
      };
    }

    if ("slug" in navLink) {
      const article = await this.getArticle(navLink.slug);
      if (!article) {
        throw new Error(`Doc not found: ${navLink.slug}`);
      }
      return {
        label: navLink.label ?? article.frontmatter.title,
        link: navLink.slug,
        badge: normalizeBadge(navLink.badge),
        external: false,
      };
    }

    if ("autogenerate" in navLink) {
      const paths = Object.keys(this.#allArticles).filter((path) =>
        path.startsWith(navLink.autogenerate.directory + "/"),
      );
      const articles = (await this.getArticles(paths)) as Markdown[];
      const articlesWithPath = articles.map((article, i) => ({
        article,
        path: paths[i],
      }));

      let titleMissing = false;
      // Check frontmatter for title
      for (const { article, path } of articlesWithPath) {
        if (!article.frontmatter.title) {
          console.error(`Missing # title in doc: ${path}`);
          titleMissing = true;
        }
      }
      if (titleMissing) throw new Error("Aborting due to errors.");

      articlesWithPath.sort((a, b) => {
        const orderA = a.article.frontmatter.order;
        const orderB = b.article.frontmatter.order;
        if (orderA != null && orderB != null) {
          return orderA - orderB;
        }
        if (orderA != null) {
          return -1;
        }
        if (orderB != null) {
          return 1;
        }
        const titleA = a.article.frontmatter.title ?? a.path;
        const titleB = a.article.frontmatter.title ?? a.path;
        return titleA.localeCompare(titleB);
      });
      const items = await Promise.all(
        articlesWithPath.map(({ article, path }) =>
          this.#normalizeNavLink({
            label: article.frontmatter.title,
            link: path,
          }),
        ),
      );
      return {
        label:
          navLink.label ?? navLink.autogenerate.directory.split("/").at(-1),
        items,
        collapsed: !!navLink.collapsed,
        badge: normalizeBadge(navLink.badge),
      };
    }

    return {
      ...navLink,
      badge: normalizeBadge(navLink.badge),
      external: /^(https?:)?\/\//.test(navLink.link),
    };
  }
}

export function visitHeadings(
  headings: Heading[],
  visit: (heading: Heading, parents: Heading[]) => false | void,
): void {
  _findHeading(headings, [], visit);
}

function _findHeading(
  headings: Heading[],
  parents: Heading[],
  visit: (heading: Heading, parents: Heading[]) => false | void,
): void {
  for (const heading of headings) {
    if (visit(heading, parents) === false) {
      return;
    }
    _findHeading(heading.children, [...parents, heading], visit);
  }
}

export type RawNavLink =
  | string
  | {
      label: string;
      items: RawNavLink[];
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

export type NavLink =
  | {
      label: string;
      items: NavLink[];
      collapsed: boolean;
      badge?: Badge;
    }
  | {
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

function normalizeHeadings(headings: MarkdownHeading[]): Heading[] {
  return headings.map((heading) => ({
    ...heading,
    scrolledPast: 0,
    children: normalizeHeadings(heading.children),
  })) as Heading[];
}
