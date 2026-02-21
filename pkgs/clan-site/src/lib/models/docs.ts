import type { DocsPath } from "$config";
import type { TocItem } from "@clan/md-svelte";
import config from "$config";

export type NavPath = readonly number[];
export type NavItem = NavGroup | NavPathItem | NavURLItem;
export type NavItems = readonly NavItem[];

export interface NavGroup {
  readonly label: string;
  readonly children: NavItems;
  readonly path: DocsPath;
}

export interface NavPathItem {
  readonly label: string;
  readonly path: DocsPath;
}

export interface NavURLItem {
  readonly label: string;
  readonly url: string;
}

export interface NavSibling {
  readonly label: string;
  readonly path: DocsPath;
}

export type Toc = readonly TocItem[];
export type { TocItem };

export interface Article {
  readonly toc: Toc;
  readonly navPath: NavPath;
  readonly prev?: NavSibling;
  readonly next?: NavSibling;
}

export function toDocsPath(path: string): DocsPath {
  return `${config.docsBase}${path ? `/${path}` : ""}`;
}
