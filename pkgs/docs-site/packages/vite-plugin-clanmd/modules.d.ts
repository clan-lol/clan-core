import type { Extension as FromMarkdownExtension } from "mdast-util-from-markdown";
import type { Heading } from "./index.ts";
import type { Extension as MicromarkExtensions } from "micromark-extension-gfm";

declare module "vfile" {
  interface DataMap {
    matter: Frontmatter;
    toc: Heading[];
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
    extensions: MicromarkExtensions[];
  }
}

declare module "hast" {
  interface ElementContentMap {
    code: Element;
  }
  interface Properties {
    class?: string;
  }
}

export interface Frontmatter {
  title: string;
  [k: string]: unknown;
}
