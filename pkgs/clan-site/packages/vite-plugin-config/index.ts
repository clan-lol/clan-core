import type { PluginOption } from "vite";
import pkg from "./package.json" with { type: "json" };

export default function vitePluginConfig(opts: {
  config: unknown;
}): PluginOption {
  const virtualModuleId = "$config";
  return {
    name: pkg.name,
    resolveId(id) {
      if (id === virtualModuleId) {
        return id;
      }
      return null;
    },
    load(id) {
      if (id === virtualModuleId) {
        return `export default ${JSON.stringify(opts.config)}`;
      }
      return null;
    },
  };
}
