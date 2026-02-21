import type { Extension as FromMarkdownExtension } from "mdast-util-from-markdown";
import type { Extension as MicromarkExtensions } from "micromark-extension-gfm";
import type { TocItem } from "./index.ts";

declare module "vfile" {
  interface DataMap {
    matter: Record<string, unknown>;
    title: string;
    toc: readonly TocItem[];
    svelteComponents: Set<string>;
  }
}

declare module "unified" {
  interface Data {
    micromarkExtensions?: MicromarkExtensions[];
    fromMarkdownExtensions?: FromMarkdownExtension[];
  }
}
declare module "mdast-util-from-markdown" {
  interface Options {
    readonly extensions: MicromarkExtensions[];
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
