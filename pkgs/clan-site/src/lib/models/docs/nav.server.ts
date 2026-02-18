import type { Badge, NavItem, NavPathItem, NavSibling } from "./nav.ts";
import type {
  Badge as BadgeInput,
  DocsPath,
  NavItem as NavItemInput,
  Path,
} from "$config";
import config from "$config";
import {
  loadMarkdown,
  recursiveLoadMarkdowns,
  toDocsPath,
} from "./docs.server.ts";
import { visit } from "$lib/util.ts";

export async function getNavItems(): Promise<readonly NavItem[]> {
  return await normalizeNavItems(config.docsNav);
}

export function normalizeBadge(
  badge: BadgeInput | undefined,
): Badge | undefined {
  if (badge === undefined || badge === "") {
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
      path: toDocsPath(navItem),
      badge: undefined,
    };
  }

  if ("children" in navItem) {
    const children = await normalizeNavItems(navItem.children);
    const pathItem = findFirstNavPathItem(children);
    if (!pathItem) {
      throw new Error(`Nav group ${navItem.label} contains no path item`);
    }
    return {
      label: navItem.label,
      path: pathItem.path,
      badge: normalizeBadge(navItem.badge),
      children,
    };
  }

  if ("slug" in navItem) {
    const md = await loadMarkdown(navItem.slug);
    return {
      label: navItem.label ?? md.frontmatter.title,
      path: toDocsPath(navItem.slug),
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
      children: items,
      path: navPath.path,
      badge: normalizeBadge(navItem.badge),
    };
  }
  if ("path" in navItem) {
    return {
      label: navItem.label,
      path: toDocsPath(navItem.path),
      badge: normalizeBadge(navItem.badge),
    };
  }
  return {
    label: navItem.label,
    url: navItem.url,
  };
}

export function getNavPath(
  navItems: readonly NavItem[],
  path: DocsPath,
): readonly number[] {
  const navPath: number[] = [];
  visit(navItems, (navItem, i, parents) => {
    if ("children" in navItem || !("path" in navItem)) {
      return;
    }
    if (navItem.path === path) {
      navPath.push(...parents.map((parent) => parent.index), i);
    }
  });
  return navPath;
}

export function findNavSiblings(
  navItems: readonly NavItem[],
  path: DocsPath,
): readonly [NavSibling | undefined, NavSibling | undefined] {
  let index = -1;
  const pathItems: NavPathItem[] = [];
  let prev: NavSibling | undefined;
  let next: NavSibling | undefined;
  visit(navItems, (navItem) => {
    if ("children" in navItem || !("path" in navItem)) {
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
      pathItems.push(navItem);
      return;
    }
    index = pathItems.length;
    pathItems.push(navItem);
    const navPath = pathItems[index - 1];
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
    if ("children" in navItem) {
      const item = findFirstNavPathItem(navItem.children);
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
