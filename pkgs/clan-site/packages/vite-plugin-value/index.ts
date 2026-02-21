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
    resolveId(source) {
      if (source === specifier) {
        return `\0${specifier}`;
      }
      return;
    },
    load(id) {
      if (id === `\0${specifier}`) {
        return `export default ${JSON.stringify(value)}`;
      }
      return;
    },
  };
}
