import type { PluginOption } from "vite";
import pathutl from "node:path";
import pkg from "./package.json" with { type: "json" };
import { rm } from "node:fs/promises";

export default function vitePluginRm({
  paths,
}: {
  paths: string[];
}): PluginOption {
  let root: string;
  let ssr: string | boolean;
  return {
    name: pkg.name,
    apply: "build",
    configResolved(config): void {
      ({ root } = config);
      ({ ssr } = config.build);
    },
    closeBundle: {
      sequential: true,
      async handler(): Promise<void> {
        if (ssr === false || ssr === "") {
          return;
        }
        await Promise.all(
          paths.map(async (path) => {
            const p = pathutl.resolve(root, path);
            await rm(p, { recursive: true });
          }),
        );
      },
    },
  };
}
