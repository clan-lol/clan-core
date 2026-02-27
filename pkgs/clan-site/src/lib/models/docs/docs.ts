import type { NavPointer, NavSibling } from "./nav.ts";
import type { TocItemsInput } from "./toc.ts";
import { docsBase } from "$config";

export type DocsPath = `/docs/${string}`;

export type MastheadMode = "search" | "nav" | false;

export interface ArticleInput {
  readonly toc: TocItemsInput;
  readonly navPointer: NavPointer;
  readonly prev?: NavSibling;
  readonly next?: NavSibling;
}

export function toDocsPath(path: string): DocsPath {
  if (!path) {
    return docsBase;
  }
  return `${docsBase}/${path}`;
}
