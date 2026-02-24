import type {
  DocsPath,
  DocsNavItem as NavItemInput,
  DocsNavItems as NavItemsInput,
} from "../clan-site.config.ts";
import type {
  NavItem,
  NavItems,
  NavPath,
  NavPathItem,
  NavSibling,
} from "../src/lib/models/docs.ts";
import config from "../clan-site.config.ts";
import { visit } from "../src/lib/util.ts";

export async function getNavItems(
  titles: Readonly<Record<string, string>>,
): Promise<NavItems> {
  return await normalizeNavItems(config.docsNav, titles);
}

export async function normalizeNavItems(
  navItems: NavItemsInput,
  titles: Readonly<Record<string, string>>,
): Promise<NavItems> {
  return await Promise.all(
    navItems.map(async (navItem) => await normalizeNavItem(navItem, titles)),
  );
}

export async function normalizeNavItem(
  navItem: NavItemInput,
  titles: Readonly<Record<string, string>>,
): Promise<NavItem> {
  if (typeof navItem === "string") {
    return {
      label: titles[navItem] ?? "",
      path: toDocsPath(navItem),
    };
  }

  if ("children" in navItem) {
    const children = await normalizeNavItems(navItem.children, titles);
    const pathItem = findFirstNavPathItem(children);
    if (!pathItem) {
      throw new Error(`Nav group ${navItem.label} contains no path item`);
    }
    return {
      label: navItem.label,
      path: pathItem.path,
      children,
    };
  }

  if ("path" in navItem) {
    return {
      label: navItem.label,
      path: toDocsPath(navItem.path),
    };
  }

  return {
    label: navItem.label,
    url: navItem.url,
  };
}

export function getNavPath(navItems: NavItems, path: string): NavPath {
  const navPath: number[] = [];
  visit(navItems, (navItem, i, parents) => {
    if ("children" in navItem || !("path" in navItem)) {
      return;
    }
    if (navItem.path === toDocsPath(path)) {
      navPath.push(...parents.map((parent) => parent.index), i);
    }
  });
  return navPath;
}

export function findNavSiblings(
  navItems: NavItems,
  path: string,
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
    pathItems.push(navItem);
    if (navItem.path !== toDocsPath(path)) {
      return;
    }
    index = pathItems.length - 1;
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
  navItems: NavItems,
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

function toDocsPath(path: string): DocsPath {
  return `${config.docsBase}${path ? `/${path}` : ""}`;
}
