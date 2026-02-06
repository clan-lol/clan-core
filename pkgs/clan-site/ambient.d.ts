declare module "$config" {
  import type { Badge, Config, NavItem, Path } from "./clan-site.config.ts";

  export type { Badge, Config, NavItem, Path };
  const config: Config;
  export default config;
}

export {};
