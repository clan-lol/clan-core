import { readFile } from "node:fs/promises";

export async function getVersion(): Promise<string> {
  const url = new URL("../../../../../VERSION", import.meta.url);
  const content = await readFile(url, "utf8");
  return content.trim();
}
