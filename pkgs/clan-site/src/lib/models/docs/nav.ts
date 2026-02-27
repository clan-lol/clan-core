import type { DocsPath } from "./docs.ts";

export type NavItemsConfig = readonly NavItemConfig[];
export type NavItemConfig =
  | string
  | {
      readonly label: string;
      readonly open?: boolean;
      readonly children: NavItemsConfig;
    }
  | {
      readonly label: string;
      readonly path: string;
    }
  | {
      readonly label: string;
      readonly url: string;
    };

export type NavPointer = readonly number[];
export type NavItemInput = NavGroupInput | NavPathItemInput | NavURLItemInput;
export type NavItemsInput = readonly NavItemInput[];

export interface NavGroupInput {
  readonly label: string;
  readonly open: boolean;
  readonly children: NavItemsInput;
}

export interface NavPathItemInput {
  readonly label: string;
  readonly path: DocsPath;
}

export interface NavURLItemInput {
  readonly label: string;
  readonly url: string;
}

export interface NavSibling {
  readonly label: string;
  readonly path: DocsPath;
}
