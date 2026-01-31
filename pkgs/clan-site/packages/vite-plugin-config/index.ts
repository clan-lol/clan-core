import type { PluginOption } from "vite";
import pkg from "./package.json" with { type: "json" };

export default function vitePluginConfig(opts: {
  config: unknown;
}): PluginOption {
  const virtualModuleId = "$config";
  const resolvedVirtualModuleId = `\0${virtualModuleId}`;
  return {
    name: pkg.name,
    resolveId(id) {
      if (id === virtualModuleId) {
        return resolvedVirtualModuleId;
      }
      return null;
    },
    load(id) {
      if (id === resolvedVirtualModuleId) {
        return `export default ${JSON.stringify(opts.config)}`;
      }
      return null;
    },
  };
}
