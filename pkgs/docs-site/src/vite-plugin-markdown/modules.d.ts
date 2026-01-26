declare module "hast" {
  interface ElementContentMap {
    code: Element;
  }
  interface Properties {
    class?: string;
  }
}

declare module "vfile" {
  interface DataMap {
    matter: Record<string, unknown>;
  }
}

export {};
