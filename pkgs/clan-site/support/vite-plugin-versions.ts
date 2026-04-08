import type { PluginOption } from "vite";
import { createReadStream } from "node:fs";
import pathutil from "node:path";

export default function vitePluginVersions(): PluginOption {
  return {
    name: "vite-plugin-versions",
    configureServer(server): void {
      server.middlewares.use((req, res, next) => {
        if (req.url !== "/docs/versions") {
          next();
          return;
        }
        const path = pathutil.resolve(import.meta.dirname, "../versions");
        const readStream = createReadStream(path);
        readStream.pipe(res);
      });
    },
  };
}
