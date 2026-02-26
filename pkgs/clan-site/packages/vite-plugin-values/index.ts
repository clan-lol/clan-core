import type { PluginOption } from "vite";
import pkg from "./package.json" with { type: "json" };

export default function vitePluginValue({
  specifier,
  value,
}: {
  specifier: string;
  value: object;
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
      if (id !== `\0${specifier}`) {
        return;
      }
      return Object.entries(value)
        .map(([k, v]) => `export const ${k} = ${JSON.stringify(v)}`)
        .join(";\n");
    },
  };
}
