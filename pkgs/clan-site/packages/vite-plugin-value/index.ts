import type { PluginOption } from "vite";
import pkg from "./package.json" with { type: "json" };

export default function vitePluginConfig({
  name: moduleId,
  value,
}: {
  name: string;
  value: unknown;
}): PluginOption {
  return {
    name: pkg.name,
    resolveId(id) {
      if (id === moduleId) {
        return id;
      }
      return null;
    },
    load(id) {
      if (id === moduleId) {
        return `export default ${JSON.stringify(value)}`;
      }
      return null;
    },
  };
}
