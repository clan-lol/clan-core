// There is an existing pagefind plugin for vite:
// https://github.com/Hugos68/vite-plugin-pagefind
//
// It's not used becuase:
// 1. It manually run the package manager's build command. This mean it needs to
//    detech which package manager is actually used, where it could have simply
//    run the pagefind's node API at vite build time and asks the user to run
//    the build command in the dev command.
// 2. It expects the build command to specify the output directory and then the
//    corresponding option passes to the vite plugin must match that value. This
//    means there are two sources of truth.
// 3. It can't do multiple plugin instances to index different folders

import type { PagefindServiceConfig } from "pagefind";
import type { PluginOption } from "vite";
import * as pagefind from "pagefind";
import pathutil from "node:path";
import pkg from "./package.json" with { type: "json" };
import { rm } from "node:fs/promises";

/* eslint-disable @typescript-eslint/naming-convention */
export interface PagefindIndexOptions {
  basePath?: string;
  baseUrl?: string;
  excerptLength?: number;
  indexWeight?: number;
  mergeFilter?: Record<string, unknown>;
  highlightParam?: string;
  language?: string;
  primary?: boolean;
  ranking?: PagefindRankingWeights;
}

export interface PagefindRankingWeights {
  termSimilarity?: number;
  pageLength?: number;
  termSaturation?: number;
  termFrequency?: number;
}

export interface PagefindSearchOptions {
  preload?: boolean;
  verbose?: boolean;
  filters?: Record<string, unknown>;
  sort?: Record<string, unknown>;
}

export type PagefindFilterCounts = Record<string, Record<string, number>>;

export interface PagefindSearchResults {
  results: PagefindSearchResult[];
  unfilteredResultCount: number;
  filters: PagefindFilterCounts;
  totalFilters: PagefindFilterCounts;
  timings: {
    preload: number;
    search: number;
    total: number;
  };
}

export interface PagefindSearchResult {
  id: string;
  score: number;
  words: number[];
  data: () => Promise<PagefindSearchFragment>;
}

export interface PagefindSearchFragment {
  url: string;
  raw_url?: string;
  content: string;
  raw_content?: string;
  excerpt: string;
  sub_results: PagefindSubResult[];
  word_count: number;
  locations: number[];
  weighted_locations: PagefindWordLocation[];
  filters: Record<string, string[]>;
  meta: Record<string, string>;
  anchors: PagefindSearchAnchor[];
}

export interface PagefindSubResult {
  title: string;
  url: string;
  locations: number[];
  weighted_locations: PagefindWordLocation[];
  excerpt: string;
  anchor?: PagefindSearchAnchor;
}

export interface PagefindWordLocation {
  weight: number;
  balanced_score: number;
  location: number;
}

export interface PagefindSearchAnchor {
  element: string;
  id: string;
  text?: string;
  location: number;
}
/* eslint-enable @typescript-eslint/naming-convention */

export interface Pagefind {
  debouncedSearch: (
    query: string,
    options?: PagefindSearchOptions,
    duration?: number,
  ) => Promise<PagefindSearchResults>;
  destroy: () => Promise<void>;
  filters: () => Promise<PagefindFilterCounts>;
  init: () => Promise<void>;
  mergeIndex: (
    indexPath: string,
    options?: Record<string, unknown>,
  ) => Promise<void>;
  options: (options: PagefindIndexOptions) => Promise<void>;
  preload: (term: string, options?: PagefindIndexOptions) => Promise<void>;
  search: (
    term: string,
    options?: PagefindSearchOptions,
  ) => Promise<PagefindSearchResults>;
}
export interface VitePluginPagefindOptions {
  pluginInstance?: string;
  siteDir?: string;
  staticDir?: string;
  assetsDir?: string;
  bundleDir?: string;
  base?: string;
  pagefindOptions?: PagefindServiceConfig & {
    glob?: string;
  };
}

export default function vitePluginPagefind({
  pluginInstance,
  siteDir = "build",
  staticDir = "static",
  assetsDir = "",
  bundleDir = "pagefind",
  base = "/",
  pagefindOptions,
}: VitePluginPagefindOptions): PluginOption {
  let root: string;
  let mode: string;
  return {
    name: `${pkg.name}${pluginInstance ? `-${pluginInstance}` : ""}`,
    apply: "build",
    config(_config, { mode: m }) {
      mode = m;
      return {
        assetsInclude: ["**/pagefind.js", "**/pagefind-highlight.js"],
        build: {
          rollupOptions: {
            external: [
              `${base}${bundleDir}/pagefind.js`,
              `${base}${bundleDir}/pagefind-highlight.js`,
            ],
          },
        },
      };
    },
    async configResolved(config) {
      ({ root } = config);
      if (mode === "production") {
        await rm(pathutil.resolve(root, staticDir, bundleDir), {
          recursive: true,
          force: true,
        });
      }
    },
    closeBundle: {
      sequential: true,
      async handler() {
        const { glob, ...pfOpts } = pagefindOptions ?? {};

        // Create a Pagefind search index to work with
        const { index, errors } = await pagefind.createIndex(pfOpts);
        if (!index) {
          throw new Error(
            `Failed to create pagefind index:\n${errors.join("\n")}`,
          );
        }

        await index.addDirectory({
          path: pathutil.resolve(root, siteDir),
          ...(glob ? { glob } : {}),
        });
        // Await rm(bundleInStatic, { recursive: true, force: true });
        await index.writeFiles({
          outputPath:
            mode === "development"
              ? pathutil.resolve(root, staticDir, bundleDir)
              : pathutil.resolve(root, assetsDir, bundleDir),
        });
      },
    },
  };
}
