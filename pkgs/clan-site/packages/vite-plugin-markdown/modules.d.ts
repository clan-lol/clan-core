import type { Extension as FromMarkdownExtension } from "mdast-util-from-markdown";
import type { FrontmatterInput, HeadingInput } from "./index.ts";
import type { Extension as MicromarkExtensions } from "micromark-extension-gfm";

declare module "vfile" {
  interface DataMap {
    matter: FrontmatterInput;
    toc: HeadingInput[];
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

export {};
