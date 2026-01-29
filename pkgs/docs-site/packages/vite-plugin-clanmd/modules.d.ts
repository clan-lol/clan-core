import type { Extension as FromMarkdownExtension } from "mdast-util-from-markdown";
import type { Extension as MicromarkExtensions } from "micromark-extension-gfm";

export interface Frontmatter {
  [k: string]: unknown;
  title: string;
}

export interface Heading {
  id: string;
  content: string;
  children: Heading[];
}
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
    readonly extensions: MicromarkExtensions[];
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
