import type { ArticleInput, DocsPath } from "./docs.ts";
import type { NavItemsInput } from "./nav.ts";
import {
  asyncMapObjectKeyValues,
  asyncMapObjectValues,
  mapObjectValues,
} from "#lib/util.ts";
import * as config from "#config";
import { mkdir, opendir, readFile, rm, writeFile } from "node:fs/promises";
import pathutil from "node:path";
import { ServerNav } from "./nav.server.ts";
import * as sveltemd from "@clan.lol/svelte-md";

const componentsSpecifierPrefix = "$lib/components";
const articlesDir = pathutil.resolve(
  import.meta.dirname,
  "../../../routes/(docs)/docs/[ver]/",
);
const layoutDir = pathutil.resolve(
  import.meta.dirname,
  "../../../routes/(docs)/",
);

export const versionedBase: DocsPath = `${config.docsBase}/${config.version}`;

// This is identical to the same function in ./docs.svelte.ts, but this
// implementation uses values supported by nodejs
export function toDocsPath(path: string): DocsPath {
  if (!path) {
    return versionedBase;
  }
  return `${versionedBase}/${path}`;
}

export class ServerDocs {
  public static async init(): Promise<ServerDocs> {
    const docs = new ServerDocs(config.docsSrcDirs);
    await docs.#renderAllFiles();
    return docs;
  }

  public paths: Record<string, string | undefined> = {};
  public titles: Record<string, string | undefined> = {};
  public nav!: ServerNav;
  #dirs: readonly string[];

  private constructor(dirs: readonly string[]) {
    this.#dirs = dirs;
  }

  public async renderFile(filename: string): Promise<void> {
    const path = this.paths[filename];
    if (path === undefined) {
      return;
    }
    const output = await compileFile(filename);
    await this.#writeFile(path, output);
  }

  public async removeFile(filename: string): Promise<void> {
    const path = this.paths[filename];
    if (!path) {
      return;
    }
    this.paths[filename] = undefined;
    this.titles[filename] = undefined;
    const dir = pathutil.join(articlesDir, path);
    await Promise.all([
      rm(pathutil.join(dir, "+page.ts")),
      rm(pathutil.join(dir, "+page.svelte")),
    ]);
  }

  async #renderAllFiles(): Promise<void> {
    const paths: Record<string, string> = {};
    for (const dir of this.#dirs) {
      // eslint-disable-next-line no-await-in-loop
      for await (const dirent of await opendir(dir, { recursive: true })) {
        if (!dirent.isFile()) {
          continue;
        }
        let name: string;
        if (dirent.name.endsWith(".md")) {
          name = dirent.name.slice(0, -".md".length);
        } else if (dirent.name.endsWith(".svelte")) {
          name = dirent.name.slice(0, -".svelte".length);
        } else {
          continue;
        }
        if (name === "index") {
          name = "";
        }
        const filename = pathutil.join(dirent.parentPath, dirent.name);
        if (filename in this.paths) {
          continue;
        }
        const base = pathutil.relative(dir, dirent.parentPath);
        const path = !base && !name ? "" : pathutil.join(base, name);
        paths[filename] = path;
      }
    }

    const outputs = await asyncMapObjectKeyValues(
      paths,
      async ([filename, path]) => [path, await compileFile(filename)],
    );
    this.paths = paths;
    this.titles = mapObjectValues(outputs, ([, output]) => output.title);
    this.nav = await ServerNav.init(this);

    await Promise.all([
      asyncMapObjectValues(outputs, async ([path, output]) => {
        await this.#writeFile(path, output);
      }),
      writeFile(
        pathutil.join(layoutDir, "+layout.ts"),
        layoutContent(this.nav.items),
      ),
    ]);
  }

  async #writeFile(path: string, output: sveltemd.Output): Promise<void> {
    const dir = pathutil.join(articlesDir, path);
    await mkdir(dir, { recursive: true });
    await Promise.all([
      writeFile(
        pathutil.join(dir, "+page.ts"),
        this.#pageContent(path, output),
      ),
      writeFile(pathutil.join(dir, "+page.svelte"), pageSvelteContent(output)),
    ]);
  }

  #pageContent(path: string, output: sveltemd.Output): string {
    const [prev, next] = this.nav.getSiblings(path);
    const navPointer = this.nav.getPointer(path);
    const article: ArticleInput = {
      title: output.title,
      toc: output.frontmatter["toc"] === false ? [] : output.toc,
      navPointer,
      ...(prev ? { prev } : {}),
      ...(next ? { next } : {}),
    };
    return `
import type { ArticleInput } from "$lib/models/docs.ts";
import type { PageLoad } from "./$types.ts";

export const load: PageLoad = (): ArticleInput => (${JSON.stringify(article)});
`;
  }
}

function pageSvelteContent(output: sveltemd.Output): string {
  const imports = [...output.svelteComponents]
    .map(
      (name) =>
        `  import ${name} from ${JSON.stringify(`${componentsSpecifierPrefix}/${name}.svelte`)}`,
    )
    .join(";\n");
  return `
  ${
    imports.length === 0
      ? ""
      : `
  <script lang="ts">
  ${imports}
  </script>`
  }
  ${output.markup}
  `;
}

function layoutContent(navItems: NavItemsInput): string {
  return `
import type { LayoutLoad } from "./$types.ts";
import type { NavItemsInput } from "$lib/models/docs.ts";

export const load: LayoutLoad = (): { navItems: NavItemsInput } => (${JSON.stringify({ navItems })});
`;
}

async function compileFile(filename: string): Promise<sveltemd.Output> {
  return filename.endsWith(".md")
    ? await compileMarkdownFile(filename)
    : await compileSvelteFile(filename);
}

async function compileMarkdownFile(filename: string): Promise<sveltemd.Output> {
  let source = await readFile(filename, { encoding: "utf8" });
  source = source.replaceAll("```shellSession", "```console");
  source = source.replaceAll("'/dev/sd<X>'", "`/dev/sd<X>`");
  source = source.replaceAll(
    /<div\sclass="grid cards"\smarkdown>(?<md>.+?)<\/div>/gs,
    "$1",
  );
  source = replaceCodeLang(source, filename);
  source = replaceButtonSyntax(source);
  const output = await sveltemd.compile(source, {
    root: pathutil.dirname(import.meta.dirname),
    filename,
    codeLightTheme: config.codeLightTheme,
    codeDarkTheme: config.codeDarkTheme,
    minLineNumberLines: config.codeMinLineNumberLines,
    maxTocDepth: config.maxTocDepth,
    codeEmbedDir: config.docsCodeEmbedsDir,
  });
  return output;
}

async function compileSvelteFile(filename: string): Promise<sveltemd.Output> {
  const content = await readFile(filename, { encoding: "utf8" });
  const result = /<h1[^>]*>(?<title>.+?)<\/h1>/s.exec(content);
  const title = result?.groups?.["title"];
  if (!title) {
    throw new Error(`Missing <h1>: ${filename}`);
  }

  return {
    title,
    frontmatter: {},
    svelteComponents: new Set(),
    markup: content,
    toc: [],
  };
}

function replaceCodeLang(source: string, filename: string): string {
  return source.replaceAll(
    /```\{(?<content>[^}]+)\}/g,
    (match, content: string): string => {
      let result = /^\s*\.(?<lang>[-a-zA-Z]+)/.exec(content);
      let lang = result?.groups?.["lang"];
      if (!lang) {
        throw new Error(`Can't find code block lang: ${match} ${filename}`);
      }
      switch (lang) {
        case "text":
        case "no-copy": {
          lang = "";
          break;
        }
        case "shellSession": {
          lang = "console";
          break;
        }
        default: {
          break;
        }
      }
      result = /hl_lines="(?<hl>[^"]+)"/.exec(content);
      let hl = result?.groups?.["hl"] ?? "";
      hl = hl.split(/\s+/).join(",");
      return `\`\`\`${lang}${hl ? ` {${hl}}` : ""}`;
    },
  );
}

function replaceButtonSyntax(source: string): string {
  return source.replaceAll(
    /\[(?<title>[^\]]+)\]\((?<url>[^)]+)\)\{(?<html>[^}]+)\}/g,
    (_match, title: string, url: string) => `[${title}](${url})`,
  );
}
