import type { PluginOption } from "vite";
import pkg from "./package.json" with { type: "json" };

export default function vitePluginConfig({
  specifier,
  value,
}: {
  specifier: string;
  value: unknown;
}): PluginOption {
  return {
    name: pkg.name,
    resolveId(id) {
      if (id === specifier) {
        return id;
      }
      return null;
    },
    load(id) {
      if (id === specifier) {
        return `export default ${JSON.stringify(value)}`;
      }
      return null;
    },
  };
}
