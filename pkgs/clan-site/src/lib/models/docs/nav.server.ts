import type {
  NavItemConfig,
  NavItemInput,
  NavItemsConfig,
  NavItemsInput,
  NavPathItemInput,
  NavPointer,
  NavSibling,
} from "#lib/models/docs.ts";
import type { ServerDocs } from "./docs.server.ts";
import { docsNav } from "#config";
import { toDocsPath } from "./docs.server.ts";
import { visit } from "#lib/util.ts";

export class ServerNav {
  public static async init(docs: ServerDocs): Promise<ServerNav> {
    const nav = new ServerNav(docs);
    nav.#items = await nav.#toNavItems(docsNav);
    return nav;
  }

  #docs: ServerDocs;
  #items!: NavItemsInput;
  public get items(): NavItemsInput {
    return this.#items;
  }
  private constructor(docs: ServerDocs) {
    this.#docs = docs;
  }

  public getPointer(path: string): NavPointer {
    const pointer: number[] = [];
    visit(this.#items, (navItem, i, parents) => {
      if ("children" in navItem || !("path" in navItem)) {
        return;
      }
      if (navItem.path === toDocsPath(path)) {
        pointer.push(...parents.map((parent) => parent.index), i);
      }
    });
    return pointer;
  }

  public getSiblings(
    path: string,
  ): readonly [NavSibling | undefined, NavSibling | undefined] {
    let index = -1;
    const pathItems: NavPathItemInput[] = [];
    let prev: NavSibling | undefined;
    let next: NavSibling | undefined;
    visit(this.#items, (navItem) => {
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

  async #toNavItems(navItems: NavItemsConfig): Promise<NavItemsInput> {
    return await Promise.all(
      navItems.map(async (navItem) => await this.#toNavItem(navItem)),
    );
  }

  async #toNavItem(navItem: NavItemConfig): Promise<NavItemInput> {
    if (typeof navItem === "string") {
      return {
        label: this.#docs.pathTitleMap[navItem] || "<Missing Page>",
        path: toDocsPath(navItem),
      };
    }

    if ("children" in navItem) {
      const children = await this.#toNavItems(navItem.children);
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

    if ("pathPrefix" in navItem) {
      return {
        label: navItem.label,
        open: false,
        children: this.#import(navItem.pathPrefix),
      };
    }

    return {
      label: navItem.label,
      url: navItem.url,
    };
  }

  #import(pathPrefix: string): NavItemsInput {
    const paths = Object.values(this.#docs.filenamePathMap).filter(
      (path) =>
        path !== undefined &&
        (path === pathPrefix || path.startsWith(`${pathPrefix}/`)),
    ) as string[];
    return paths
      .toSorted((a, b) => a.localeCompare(b))
      .map((path) => ({
        label: this.#docs.pathTitleMap[path] || "<Missing Page>",
        path: toDocsPath(path),
      }));
  }
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
