import type { TocItem } from "./index.ts";

declare module "vfile" {
  interface DataMap {
    matter: Record<string, unknown>;
    title: string;
    toc: readonly TocItem[];
    svelteComponents: Set<string>;
  }
}

declare module "hast" {
  interface ElementContentMap {
    code: Element;
  }
  interface Properties {
    id?: string;
    class?: string;
  }
}
