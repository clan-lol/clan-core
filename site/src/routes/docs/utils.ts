export const articles = Object.fromEntries(
  Object.entries(
    import.meta.glob<{
      content: string;
      frontmatter: Record<string, any>;
      toc: string;
    }>("./**/*.md"),
  ).map(([key, fn]) => [key.slice("./".length, -".md".length), fn]),
);

export type NavLink =
  | string
  | {
      label: string;
      items: NavLink[];
      collapsed?: boolean;
      badge?: Badge;
    }
  | {
      label?: string;
      slug: string;
      badge?: Badge;
    }
  | {
      label: string;
      link: string;
      badge?: Badge;
    };

export type NormalizedNavLink =
  | {
      label: string;
      items: NormalizedNavLink[];
      collapsed: boolean;
      badge?: NormalizedBadge;
    }
  | {
      label: string;
      link: string;
      badge?: NormalizedBadge;
      external: boolean;
    };

export type Badge = string | NormalizedBadge;

export type NormalizedBadge = {
  text: string;
  variant: "caution" | "normal";
};

export async function normalizeNavLinks(
  navLinks: NavLink[],
): Promise<NormalizedNavLink[]> {
  return await Promise.all(navLinks.map(normalizeNavLink));
}

export async function normalizeNavLink(
  navLink: NavLink,
): Promise<NormalizedNavLink> {
  if (typeof navLink === "string") {
    const article = articles[navLink];
    if (!article) {
      throw new Error(`Doc not found: ${navLink}`);
    }
    return {
      label: (await article()).frontmatter.title,
      link: `/docs/${navLink}`,
      external: false,
    };
  }

  if (!("items" in navLink)) {
    if ("slug" in navLink) {
      const article = articles[`/docs/${navLink.slug}`];
      if (!article) {
        throw new Error(`Doc not found: ${navLink}`);
      }
      return {
        label: navLink.label ?? (await article()).frontmatter.title,
        link: `/docs/${navLink.slug}`,
        badge: normalizeBadge(navLink.badge),
        external: false,
      };
    }
    return {
      ...navLink,
      badge: normalizeBadge(navLink.badge),
      external: /^https?:\/\//.test(navLink.link),
    };
  }

  return {
    ...navLink,
    collapsed: !!navLink.collapsed,
    badge: normalizeBadge(navLink.badge),
    items: await Promise.all(navLink.items.map(normalizeNavLink)),
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
