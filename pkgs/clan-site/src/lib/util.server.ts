import pathutil from "node:path";
import { readFile } from "node:fs/promises";

export * from "./util/custom-media.server.ts";

export async function getVersion(): Promise<string> {
  const path = pathutil.resolve(import.meta.dirname, "../../../../VERSION");
  const content = await readFile(path, "utf8");
  return content.trim();
}

export function getGeneratedDocsDir(): string {
  const dir = process.env["GENERATED_DOCS"];
  if (!dir) {
    throw new Error("Environment variable GENERATED_DOCS is not set");
  }
  return pathutil.resolve(dir);
}
