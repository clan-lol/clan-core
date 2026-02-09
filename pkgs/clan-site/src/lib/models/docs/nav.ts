import type {
  Badge as BadgeInput,
  DocsPath,
  NavItem as NavItemInput,
  Path,
} from "$config";
import config from "$config";
import { loadMarkdown, recursiveLoadMarkdowns } from "./docs.ts";
import { visit } from "$lib/util.ts";

export type NavItem = NavGroup | NavPathItem | NavURLItem;

export interface NavGroup {
  readonly label: string;
  readonly items: readonly NavItem[];
  readonly path: DocsPath;
  readonly collapsed: boolean;
  readonly badge: Badge | undefined;
}

export interface NavPathItem {
  readonly label: string;
  readonly path: DocsPath;
  readonly badge: Badge | undefined;
}

export interface NavURLItem {
  readonly label: string;
  readonly url: string;
}

export interface NavSibling {
  readonly label: string;
  readonly path: DocsPath;
}

export type Badge = Exclude<BadgeInput, string>;

export async function getNavItems(): Promise<readonly NavItem[]> {
  return await normalizeNavItems(config.docsNav);
}

export function normalizeBadge(
  badge: BadgeInput | undefined,
): Badge | undefined {
  // TODO: typescript-eslint complains, but nullable string and nullable object
  // are allowed, figure out why it's false positive
  // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
  if (!badge) {
    return;
  }
  if (typeof badge === "string") {
    return {
      text: badge,
      variant: "normal",
    };
  }
  return badge;
}

export async function normalizeNavItems(
  navItems: readonly NavItemInput[],
): Promise<readonly NavItem[]> {
  return await Promise.all(
    navItems.map(async (navItem) => await normalizeNavItem(navItem)),
  );
}

export async function normalizeNavItem(
  navItem: NavItemInput,
): Promise<NavItem> {
  if (typeof navItem === "string") {
    const md = await loadMarkdown(navItem);
    return {
      label: md.frontmatter.title,
      path: `${config.docsBase}${navItem === "/" ? "" : navItem}` as const,
      badge: undefined,
    };
  }

  if ("items" in navItem) {
    const items = await normalizeNavItems(navItem.items);
    const pathItem = findFirstNavPathItem(items);
    if (!pathItem) {
      throw new Error(`Nav group ${navItem.label} contains no path item`);
    }
    return {
      label: navItem.label,
      path: pathItem.path,
      collapsed: Boolean(navItem.collapsed),
      badge: normalizeBadge(navItem.badge),
      items,
    };
  }

  if ("slug" in navItem) {
    const md = await loadMarkdown(navItem.slug);
    return {
      label: navItem.label ?? md.frontmatter.title,
      path: `${config.docsBase}${navItem.slug}` as const,
      badge: normalizeBadge(navItem.badge),
    };
  }

  if ("auto" in navItem) {
    const mds = await recursiveLoadMarkdowns(navItem.auto);
    const missintPaths: string[] = [];
    for (const md of mds) {
      if (!md.frontmatter.title) {
        missintPaths.push(md.path);
      }
    }
    if (missintPaths.length !== 0) {
      throw new Error(
        missintPaths
          .map((path) => `Missing # title in doc: ${path}`)
          .join("\n"),
      );
    }

    mds.sort((a, b) => {
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
      mds.map(
        async (md) =>
          await normalizeNavItem({
            label: md.frontmatter.title,
            path: md.relativePath.slice(
              config.docsDir.length,
              -".md".length,
            ) as Path,
          }),
      ),
    );
    const navPath = findFirstNavPathItem(items);
    if (!navPath) {
      throw new Error(`Nav group ${navItem.label} contains no path item`);
    }
    return {
      label: navItem.label,
      items,
      path: navPath.path,
      collapsed: Boolean(navItem.collapsed),
      badge: normalizeBadge(navItem.badge),
    };
  }
  if ("path" in navItem) {
    return {
      label: navItem.label,
      path: `${config.docsBase}${navItem.path === "/" ? "" : navItem.path}` as const,
      badge: normalizeBadge(navItem.badge),
    };
  }
  return {
    label: navItem.label,
    url: navItem.url,
  };
}

export function findNavSiblings(
  navItems: readonly NavItem[],
  path: Path,
): readonly [NavSibling | undefined, NavSibling | undefined] {
  let index = -1;
  const navPaths: NavPathItem[] = [];
  let prev: NavSibling | undefined;
  let next: NavSibling | undefined;
  visit(navItems, "items", (navItem) => {
    if (!("path" in navItem)) {
      return;
    }
    if (index !== -1) {
      next = {
        label: navItem.label,
        path: navItem.path,
      };
      return "break";
    }
    if (navItem.path !== path) {
      navPaths.push(navItem);
      return;
    }
    index = navPaths.length;
    navPaths.push(navItem);
    const navPath = navPaths[index - 1];
    if (navPath) {
      prev = {
        label: navPath.label,
        path: navPath.path,
      };
    }
    return;
  });
  return [prev, next];
}

export function findFirstNavPathItem(
  navItems: readonly NavItem[],
): NavPathItem | undefined {
  for (const navItem of navItems) {
    if ("items" in navItem) {
      const item = findFirstNavPathItem(navItem.items);
      if (item) {
        return item;
      }
      continue;
    }
    if ("path" in navItem) {
      return navItem;
    }
  }
  return;
}
