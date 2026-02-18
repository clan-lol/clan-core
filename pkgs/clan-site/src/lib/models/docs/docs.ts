import type { DocsPath } from "$config";
import type { Heading } from "@clan/vite-plugin-markdown";
import type { NavSibling } from "./nav.ts";

export type { Heading };

export interface Article {
  readonly title: string;
  readonly path: DocsPath;
  readonly content: string;
  readonly previous: NavSibling | undefined;
  readonly next: NavSibling | undefined;
  readonly navPath: readonly number[];
  readonly toc: readonly Heading[];
}
