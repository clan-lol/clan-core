import type { DocsPath } from "./docs.ts";
import { docsBase, version } from "#config";

export const versionedBase: DocsPath = `${docsBase}/${version}`;

// This is identical to the same function in ./docs.svelte.ts, but this
// implementation uses values supported by nodejs
export function toDocsPath(path: string): DocsPath {
  if (!path) {
    return versionedBase;
  }
  return `${versionedBase}/${path}`;
}
