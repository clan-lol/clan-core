import type {
  Badge as BadgeInput,
  NavItem as NavItemInput,
  Path,
} from "$config";
import type { DocsPath } from "./docs.ts";
import {
  docsBase,
  docsDir,
  loadMarkdown,
  recursiveloadMarkdowns,
} from "./docs.ts";
import { visit } from "$lib/util.ts";

export type NavItem = NavGroup | NavPath | NavURL;

export interface NavGroup {
  readonly label: string;
  readonly items: readonly NavItem[];
  readonly collapsed: boolean;
  readonly badge: Badge | null;
  isActive: boolean;
}

export interface NavPath {
  readonly label: string;
  readonly path: DocsPath;
  readonly badge: Badge | null;
  isActive: boolean;
}

export interface NavURL {
  readonly label: string;
  readonly url: string;
}

export interface NavSibling {
  readonly label: string;
  readonly path: DocsPath;
}

export type Badge = Exclude<BadgeInput, string>;

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
      path: `${docsBase}${navItem}` as const,
      badge: null,
      isActive: false,
    };
  }

  if ("items" in navItem) {
    return {
      label: navItem.label,
      collapsed: Boolean(navItem.collapsed),
      badge: normalizeBadge(navItem.badge),
      items: await normalizeNavItems(navItem.items),
      isActive: false,
    };
  }

  if ("slug" in navItem) {
    const md = await loadMarkdown(navItem.slug);
    return {
      label: navItem.label ?? md.frontmatter.title,
      path: `${docsBase}${navItem.slug}` as const,
      badge: normalizeBadge(navItem.badge),
      isActive: false,
    };
  }

  if ("recursiveImport" in navItem) {
    const mds = await recursiveloadMarkdowns(navItem.recursiveImport);

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
            url: `${docsBase}${md.relativePath.slice(docsDir.length)}`,
          }),
      ),
    );
    return {
      label: navItem.label,
      items,
      collapsed: Boolean(navItem.collapsed),
      badge: normalizeBadge(navItem.badge),
      isActive: false,
    };
  }
  if ("path" in navItem) {
    return {
      label: navItem.label,
      path: `${docsBase}${navItem.path}` as const,
      badge: normalizeBadge(navItem.badge),
      isActive: false,
    };
  }
  return {
    label: navItem.label,
    url: navItem.url,
  };
}

export function setActiveNavItems(
  navItems: readonly NavItem[],
  path: Path,
): void {
  visit(navItems, "items", (navItem, parents) => {
    if (!("isActive" in navItem) || !("path" in navItem)) {
      return;
    }
    if (navItem.path === `${docsBase}${path}`) {
      navItem.isActive = true;
      // FIXME: this type casting shouldn't be necessary, fix visit's type instead
      for (const parent of parents as readonly NavGroup[]) {
        parent.isActive = true;
      }
      return;
    }
    return;
  });
}

export function findNavSiblings(
  navItems: readonly NavItem[],
  path: Path,
): readonly [NavSibling | null, NavSibling | null] {
  let index = -1;
  const navPaths: NavPath[] = [];
  let prev: NavSibling | null = null;
  let next: NavSibling | null = null;
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
