import type {
  DocsPath,
  NavItemConfig,
  NavItemInput,
  NavItemsConfig,
  NavItemsInput,
  NavPathItemInput,
  NavPointer,
  NavSibling,
} from "#lib/models/docs.ts";
import { docsBase, docsNav } from "#config";
import { visit } from "#lib/util.ts";

export async function getNavItems(
  titles: Readonly<Record<string, string>>,
): Promise<NavItemsInput> {
  return await toNavItems(docsNav, titles);
}

export async function toNavItems(
  navItems: NavItemsConfig,
  titles: Readonly<Record<string, string>>,
): Promise<NavItemsInput> {
  return await Promise.all(
    navItems.map(async (navItem) => await toNavItem(navItem, titles)),
  );
}

export async function toNavItem(
  navItem: NavItemConfig,
  titles: Readonly<Record<string, string>>,
): Promise<NavItemInput> {
  if (typeof navItem === "string") {
    return {
      label: titles[navItem] ?? "",
      path: toDocsPath(navItem),
    };
  }

  if ("children" in navItem) {
    const children = await toNavItems(navItem.children, titles);
    return {
      label: navItem.label,
      open: Boolean(navItem.open),
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

export function getNavPointer(
  navItems: NavItemsInput,
  path: string,
): NavPointer {
  const pointer: number[] = [];
  visit(navItems, (navItem, i, parents) => {
    if ("children" in navItem || !("path" in navItem)) {
      return;
    }
    if (navItem.path === toDocsPath(path)) {
      pointer.push(...parents.map((parent) => parent.index), i);
    }
  });
  return pointer;
}

export function findNavSiblings(
  navItems: NavItemsInput,
  path: string,
): readonly [NavSibling | undefined, NavSibling | undefined] {
  let index = -1;
  const pathItems: NavPathItemInput[] = [];
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
  navItems: NavItemsInput,
): NavPathItemInput | undefined {
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

export function toDocsPath(path: string): DocsPath {
  if (!path) {
    return docsBase;
  }
  return `${docsBase}/${path}`;
}
