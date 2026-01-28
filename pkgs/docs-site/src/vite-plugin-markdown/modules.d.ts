declare module "vfile" {
  interface DataMap {
    matter: Record<string, unknown>;
  }
}

declare module "unified" {
  import type { FromMarkdownExtension } from "mdast-util-gfm";
  import type { Extension as MicromarkExtensions } from "micromark-extension-gfm";

  interface Data {
    micromarkExtensions?: MicromarkExtensions[];
    fromMarkdownExtensions?: FromMarkdownExtension[];
  }
}
declare module "mdast-util-from-markdown" {
  interface Options {
    extensions;
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
