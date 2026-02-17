/// <reference types="@poppanator/sveltekit-svg/dist/svg.d.ts" />

declare module "$config" {
  // Have to use the import() syntax because a ambient declaration file is not a module
  // https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-9.html#import-types
  type Config = import("./clan-site.config.ts");
  type Badge = import("./clan-site.config.ts").Badge;
  type NavItem = import("./clan-site.config.ts").DocsNavItem;
  type Path = import("./clan-site.config.ts").Path;
  type DocsPath = import("./clan-site.config.ts").DocsPath;

  export type { Badge, Config, DocsPath, NavItem, Path };
  const config: typeof import("./clan-site.config.ts");
  export = config;
}

// This is needed to address eslint type limitation
// https://sveltejs.github.io/eslint-plugin-svelte/user-guide/#you-re-using-type-script-and-the-imported-svelte-component-types-cannot-be-resolved-or-appear-to-be
//
// We can't use typescript-eslint-parser-for-extra-files as suggested by the FAQ because it doesn't support eslint 9
// https://github.com/ota-meshi/typescript-eslint-parser-for-extra-files/issues/162
//
// Instead we simply manually provide tht types
declare module "~/routes/(docs)/docs/[ver]/+page.svelte" {
  export const title: string;
}
