import pathutil from "node:path";
import { readFile } from "node:fs/promises";

export * from "./util/custom-media.server.ts";

export async function getVersion(): Promise<string> {
  const url = new URL("../../../../VERSION", import.meta.url);
  const content = await readFile(url, "utf8");
  return content.trim();
}

export function getGeneratedDocsDir(): string {
  const dir = process.env["GENERATED_DOCS"];
  if (!dir) {
    throw new Error("Environment variable GENERATED_DOCS is not set");
  }
  return pathutil.resolve(dir);
}
