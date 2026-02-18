import type { Badge as BadgeInput, DocsPath } from "$config";

export type NavItem = NavGroup | NavPathItem | NavURLItem;

export interface NavGroup {
  readonly label: string;
  readonly children: readonly NavItem[];
  readonly path: DocsPath;
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
