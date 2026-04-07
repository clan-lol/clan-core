import type { docsBase } from "$config";
import type { NavPointer, NavSibling } from "./nav.ts";
import type { TocItemsInput } from "./toc.ts";
import { Docs } from "./docs.svelte.ts";

export type DocsPath = `${typeof docsBase}/${string}`;

export type TopBarMode = "navBar" | "navTree" | "search";

export interface ArticleInput {
  readonly title: string;
  readonly toc: TocItemsInput;
  readonly navPointer: NavPointer;
  readonly prev?: NavSibling;
  readonly next?: NavSibling;
}

export function toDocsPath(path: string): DocsPath {
  if (!path) {
    return Docs.versionedBase;
  }
  return `${Docs.versionedBase}/${path}`;
}
