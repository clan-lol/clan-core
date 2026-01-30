declare module "eslint-plugin-promise" {
  import type { ConfigObject } from "@eslint/core";

  /* eslint-disable @typescript-eslint/naming-convention */
  const plugin: {
    configs: {
      "flat/recommended": ConfigObject;
    };
  };
  export default plugin;
}
