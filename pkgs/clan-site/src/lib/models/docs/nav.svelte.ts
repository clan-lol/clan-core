import type { Docs } from "./docs.svelte.ts";
import type { DocsPath } from "./docs.ts";
import type {
  NavGroupInput,
  NavItemsInput,
  NavPathItemInput,
  NavPointer,
  NavURLItemInput,
} from "./nav.ts";

export class Nav {
  public readonly docs: Docs;
  public readonly items: NavItems;
  public get open(): boolean {
    return this.docs.mastheadMode === "nav";
  }
  public set open(v: boolean) {
    this.docs.mastheadMode = v ? "nav" : false;
  }

  public constructor(
    items: NavItemsInput,
    pointer: () => NavPointer,
    docs: Docs,
  ) {
    this.items = new NavItems(items, pointer);
    this.docs = docs;
  }

  public toggle(): boolean {
    const open = !this.open;
    this.open = open;
    return open;
  }
}

export type NavItem = NavGroup | NavPathItem | NavURLItem;

export class NavItems extends Array<NavItem> {
  public constructor(items: NavItemsInput, pointer: () => NavPointer) {
    super(
      ...items.map((item, i) => {
        if ("children" in item) {
          return new NavGroup(item, i, pointer);
        }
        if ("path" in item) {
          return new NavPathItem(item, i, pointer);
        }
        return new NavURLItem(item);
      }),
    );
  }
}

export class NavGroup {
  public readonly label: string;
  public readonly isActive: boolean;
  public readonly children: NavItems;
  public open: boolean;
  public constructor(
    item: NavGroupInput,
    index: number,
    pointer: () => NavPointer,
  ) {
    this.label = item.label;
    this.open = $state(item.open);
    this.isActive = $derived(index === pointer()[0]);
    this.children = new NavItems(item.children, () => pointer().slice(1));
  }
}

export class NavPathItem {
  public readonly label: string;
  public readonly path: DocsPath;
  public readonly isActive: boolean;
  public constructor(
    item: NavPathItemInput,
    index: number,
    pointer: () => NavPointer,
  ) {
    this.label = item.label;
    this.path = item.path;
    this.isActive = $derived(index === pointer()[0]);
  }
}

export class NavURLItem {
  public readonly label: string;
  public readonly url: string;
  public constructor(item: NavURLItemInput) {
    this.label = item.label;
    this.url = item.url;
  }
}
