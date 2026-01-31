import type {
  Badge as BadgeInput,
  NavItem as NavItemInput,
  Path,
} from "$config";
import type { Docs } from "./docs.ts";
import { docsBase } from "./docs.ts";

export type NavItem = NavGroup | NavLink | ExternlNavLink;

export interface NavGroup {
  readonly label: string;
  readonly items: readonly NavItem[];
  readonly collapsed: boolean;
  readonly badge: Badge | null;
}

export interface NavLink {
  readonly label: string;
  readonly link: `/docs/${string}`;
  readonly external: false;
  readonly badge: Badge | null;
}

export interface ExternlNavLink {
  readonly label: string;
  readonly link: string;
  readonly external: true;
  readonly badge: Badge | null;
}

export type Badge = Exclude<BadgeInput, string>;

function isPath(s: unknown): s is Path {
  return typeof s === "string" && s.startsWith("/");
}

export function normalizeBadge(badge: BadgeInput | undefined): Badge | null {
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

export async function normalizeNavItem(
  docs: Docs,
  navItem: NavItemInput,
): Promise<NavItem> {
  if (isPath(navItem)) {
    const article = await docs.loadArticle(navItem);
    return {
      label: article.frontmatter.title,
      link: `${docsBase}${navItem}` as const,
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
          async (navItem) => await normalizeNavItem(docs, navItem),
        ),
      ),
    };
  }

  if ("slug" in navItem) {
    const article = await docs.loadArticle(navItem.slug);
    return {
      label: navItem.label ?? article.frontmatter.title,
      link: `${docsBase}${navItem.slug}` as const,
      external: false,
      badge: normalizeBadge(navItem.badge),
    };
  }

  if ("autogenerate" in navItem) {
    const articles = await docs.loadAutoGenArticle(
      navItem.autogenerate.directory,
    );

    const titleMissingArticlePaths: string[] = [];
    for (const article of articles) {
      if (!article.frontmatter.title) {
        titleMissingArticlePaths.push(article.path);
      }
    }
    if (titleMissingArticlePaths.length !== 0) {
      throw new Error(
        titleMissingArticlePaths
          .map((path) => `Missing # title in doc: ${path}`)
          .join("\n"),
      );
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
      return a.frontmatter.title.localeCompare(b.frontmatter.title);
    });
    const items = await Promise.all(
      articles.map(
        async (article) =>
          await normalizeNavItem(docs, {
            label: article.frontmatter.title,
            link: article.path,
          }),
      ),
    );
    return {
      label: navItem.label,
      items,
      collapsed: Boolean(navItem.collapsed),
      badge: normalizeBadge(navItem.badge),
    };
  }
  const external = /^(?:https?:)?\/\//.test(navItem.link);
  if (external) {
    return {
      ...navItem,
      link: navItem.link,
      badge: normalizeBadge(navItem.badge),
      external,
    };
  }
  return {
    ...navItem,
    link: `${docsBase}${navItem.link}` as const,
    badge: normalizeBadge(navItem.badge),
    external,
  };
}
