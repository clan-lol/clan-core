declare module "$config" {
  // Have to use the import() syntax because a d.ts file is not a module
  // https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-9.html#import-types
  type Config = import("./clan-site.config.ts").Config;
  type Badge = import("./clan-site.config.ts").Badge;
  type NavItem = import("./clan-site.config.ts").NavItem;
  type Path = import("./clan-site.config.ts").Path;
  type DocsPath = import("./clan-site.config.ts").DocsPath;

  export type { Badge, Config, DocsPath, NavItem, Path };
  const config: Config;
  export default config;
}
