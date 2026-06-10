import type { ArticleInput, DocsPath } from "./docs.ts";
import type { NavItemsInput } from "./nav.ts";
import {
  asyncMapObjectKeyValues,
  asyncMapObjectValues,
  mapObjectValues,
} from "#lib/util.ts";
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

type Config = typeof import("#config");

export class ServerDocs {
  public static async init(): Promise<ServerDocs> {
    // Use async import so that calling this method again reloads the config
    // file, this reloading is done by by the docs2routes vite plugin. It's
    // import to specify an absolute path, otherwise vite will fail to resolve
    // the path, probably because it does some preprocessing the vite.config.ts
    // before letting node load it
    const config = (await import(
      pathutil.resolve(
        import.meta.dirname,
        `../../../../clan-site.config.ts?t=${Date.now()}`,
      )
    )) as Config;
    const docs = new ServerDocs(config);
    await docs.#renderAllFiles();
    return docs;
  }

  public filenamePathMap: Record<string, string | undefined> = {};
  public pathTitleMap: Record<string, string | undefined> = {};
  public nav!: ServerNav;
  public readonly config: Config;
  public get versionedBase(): DocsPath {
    return `${this.config.docsBase}/${this.config.version}`;
  }

  private constructor(config: Config) {
    this.config = config;
  }

  public async renderFile(filename: string): Promise<void> {
    const path = this.filenamePathMap[filename];
    if (path === undefined) {
      return;
    }
    const output = await this.#compileFile(filename);
    if (output.title !== this.pathTitleMap[path]) {
      this.pathTitleMap[path] = output.title;
      this.nav = await ServerNav.init(this);
      await this.#writeLayoutFile();
    }
    await this.#writeFile(path, output);
  }

  public async removeFile(filename: string): Promise<void> {
    const path = this.filenamePathMap[filename];
    if (!path) {
      return;
    }
    this.filenamePathMap[filename] = undefined;
    this.pathTitleMap[path] = undefined;
    const dir = pathutil.join(articlesDir, path);
    await Promise.all([
      rm(pathutil.join(dir, "+page.ts")),
      rm(pathutil.join(dir, "+page.svelte")),
    ]);
  }

  public toDocsPath(path: string): DocsPath {
    if (!path) {
      return this.versionedBase;
    }
    return `${this.versionedBase}/${path}`;
  }

  async #renderAllFiles(): Promise<void> {
    const filenamePathMap: Record<string, string> = {};
    for (const dir of this.config.docsSrcDirs) {
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
        if (filename in this.filenamePathMap) {
          continue;
        }
        const base = pathutil.relative(dir, dirent.parentPath);
        const path = !base && !name ? "" : pathutil.join(base, name);
        filenamePathMap[filename] = path;
      }
    }

    const outputs = await asyncMapObjectKeyValues(
      filenamePathMap,
      async ([filename, path]) => [path, await this.#compileFile(filename)],
    );
    this.filenamePathMap = filenamePathMap;
    this.pathTitleMap = mapObjectValues(outputs, ([, output]) => output.title);
    this.nav = await ServerNav.init(this);

    await Promise.all([
      asyncMapObjectValues(outputs, async ([path, output]) => {
        await this.#writeFile(path, output);
      }),
      this.#writeLayoutFile(),
    ]);
  }

  async #writeLayoutFile(): Promise<void> {
    await writeFile(
      pathutil.join(layoutDir, "+layout.ts"),
      layoutContent(this.nav.items),
    );
  }

  async #writeFile(path: string, output: sveltemd.Output): Promise<void> {
    const dir =
      path === "test"
        ? pathutil.join(articlesDir, "[test=test]")
        : pathutil.join(articlesDir, path);

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

  async #compileFile(filename: string): Promise<sveltemd.Output> {
    return filename.endsWith(".md")
      ? await this.#compileMarkdownFile(filename)
      : await compileSvelteFile(filename);
  }

  async #compileMarkdownFile(filename: string): Promise<sveltemd.Output> {
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
      codeLightTheme: this.config.codeLightTheme,
      codeDarkTheme: this.config.codeDarkTheme,
      minLineNumberLines: this.config.codeMinLineNumberLines,
      maxTocDepth: this.config.maxTocDepth,
      codeEmbedDir: this.config.docsCodeEmbedsDir,
      variables: {
        version: this.config.version,
      },
    });
    return output;
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
