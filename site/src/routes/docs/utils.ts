export const articles = Object.fromEntries(
  Object.entries(
    import.meta.glob<{
      content: string;
      frontmatter: Record<string, any>;
      toc: string;
    }>("./**/*.md", { eager: true }),
  ).map(([key, fn]) => [key.slice("./".length, -".md".length), fn]),
);

export type NavLink =
  | string
  | {
      label: string;
      items: NavLink[];
      badge?: Badge;
    }
  | {
      label?: string;
      slug: string;
      badge?: Badge;
    };

export type NormalizedNavLink =
  | {
      label: string;
      items: NormalizedNavLink[];
      badge?: NormalizedBadge;
    }
  | {
      label: string;
      slug: string;
      badge?: NormalizedBadge;
    };

export type Badge = string | NormalizedBadge;

export type NormalizedBadge = {
  text: string;
  variant: "caution" | "normal";
};

export function normalizeNavLinks(navLinks: NavLink[]): NormalizedNavLink[] {
  return navLinks.map(normalizeNavLink);
}

export function normalizeNavLink(navLink: NavLink): NormalizedNavLink {
  if (typeof navLink === "string") {
    const article = articles[navLink];
    if (!article) {
      throw new Error(`Doc not found: ${navLink}`);
    }
    return {
      label: article.frontmatter.title,
      slug: `/docs/${navLink}`,
    };
  }

  if (!("items" in navLink)) {
    const article = articles[navLink.slug];
    if (!article) {
      throw new Error(`Doc not found: ${navLink}`);
    }
    return {
      ...navLink,
      label: navLink.label ?? article.frontmatter.title,
      badge: normalizeBadge(navLink.badge),
    };
  }

  return {
    ...navLink,
    badge: normalizeBadge(navLink.badge),
    items: navLink.items.map(normalizeNavLink),
  };
}

export function normalizeBadge(
  badge: Badge | undefined,
): NormalizedBadge | undefined {
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
