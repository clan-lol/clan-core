import type { ArticleInput, NavItemsInput } from "#lib/models/docs.ts";
import type { Output } from "@clan.lol/svelte-md";
import {
  asyncMapObjectKeyValues,
  asyncMapObjectValues,
  mapObjectValues,
} from "#lib/util.ts";
import * as config from "#config";
import {
  findNavSiblings,
  getNavItems,
  getNavPointer,
} from "#lib/models/docs.server.ts";
import { mkdir, opendir, readFile, writeFile } from "node:fs/promises";
import pathutil from "node:path";
import { render } from "@clan.lol/svelte-md";

const componentsSpecifierPrefix = "$lib/components";
const srcDir = "src/docs";
const articlesDir = "src/routes/(docs)/docs/[ver]";
const layoutDir = "src/routes/(docs)";

const paths: Record<string, string> = {};
for await (const dirent of await opendir(srcDir, { recursive: true })) {
  if (!dirent.isFile() || !dirent.name.endsWith(".md")) {
    continue;
  }
  const filename = pathutil.join(dirent.parentPath, dirent.name);
  switch (filename) {
    case "src/docs/api.md":
    case "src/docs/index.md": {
      continue;
    }
    default: {
      break;
    }
  }
  const base = pathutil.relative(srcDir, dirent.parentPath);
  const name = dirent.name.slice(0, -".md".length);
  const path = pathutil.join(base, name === "index" ? "" : name);
  paths[filename] = path;
}
const outputs = await asyncMapObjectKeyValues(
  paths,
  async ([filename, path]) => [path, await loadOutput(filename)],
);
const titles = mapObjectValues(outputs, ([, output]) => output.title);
const indexArticleTitle = await getIndexArticleTitle();
titles[""] = indexArticleTitle;
const navItems = await getNavItems(titles);
await Promise.all([
  asyncMapObjectValues(outputs, async ([path, output]) => {
    await writeArticle(path, output);
  }),
  writeIndexArticle(),
  writeFile(
    pathutil.join(layoutDir, "+layout.ts"),
    layoutContent({ navItems }),
  ),
]);

async function loadOutput(filename: string): Promise<Output> {
  let source = await readFile(filename, { encoding: "utf8" });
  source = source.replaceAll("```shellSession", "```console");
  source = source.replaceAll("'/dev/sd<X>'", "`/dev/sd<X>`");
  source = source.replaceAll(
    /<div\sclass="grid cards"\smarkdown>(?<md>.+?)<\/div>/gs,
    "$1",
  );
  source = replaceCodeLang(source);
  source = replaceButtonSyntax(source);
  const output = await render(source, {
    root: pathutil.dirname(import.meta.dirname),
    filename,
    codeLightTheme: config.codeLightTheme,
    codeDarkTheme: config.codeDarkTheme,
    minLineNumberLines: config.codeMinLineNumberLines,
    maxTocDepth: config.maxTocDepth,
    componentsSpecifierPrefix: "$lib/components",
    linkResolves: {
      [config.docsDir]: config.docsBase,
    },
  });
  return output;
}

async function writeArticle(path: string, output: Output): Promise<void> {
  const [prev, next] = findNavSiblings(navItems, path);
  const navPointer = getNavPointer(navItems, path);

  const dir = pathutil.join(articlesDir, path);
  await mkdir(dir, { recursive: true });
  await Promise.all([
    writeFile(
      pathutil.join(dir, "+page.ts"),
      pageContent({
        toc: output.frontmatter["toc"] === false ? [] : output.toc,
        navPointer,
        ...(prev ? { prev } : {}),
        ...(next ? { next } : {}),
      }),
    ),
    writeFile(pathutil.join(dir, "+page.svelte"), pageSvelteContent(output)),
  ]);
}

async function getIndexArticleTitle(): Promise<string> {
  const path = pathutil.join(articlesDir, "+page.svelte");
  const content = await readFile(path, { encoding: "utf8" });
  const result = /<h1[^>]*>(?<title>.+?)<\/h1>/s.exec(content);
  const title = result?.groups?.["title"];
  if (!title) {
    throw new Error(`Missing title: ${path}`);
  }
  return title;
}

async function writeIndexArticle(): Promise<void> {
  const [prev, next] = findNavSiblings(navItems, "");
  const navPointer = getNavPointer(navItems, "");
  await writeFile(
    pathutil.join(articlesDir, "+page.ts"),
    indexPageContent({
      title: indexArticleTitle,
      toc: [],
      navPointer,
      ...(prev ? { prev } : {}),
      ...(next ? { next } : {}),
    }),
  );
}

function pageContent(data: ArticleInput): string {
  return `
import type { Article } from "$lib/models/docs.ts";
import type { PageLoad } from "./$types.ts";

export const load: PageLoad = (): Article => (${JSON.stringify(data)});
`;
}

function pageSvelteContent({
  title,
  svelteComponents,
  markup,
}: Output): string {
  const imports = [...svelteComponents]
    .map(
      (name) =>
        `  import ${name} from ${JSON.stringify(`${componentsSpecifierPrefix}/${name}.svelte`)}`,
    )
    .join(";\n");
  return `
<script>
${imports}
</script>
<svelte:head>
  <title>{${JSON.stringify(title)}}</title>
</svelte:head>
${markup}
`;
}

function layoutContent(data: { navItems: NavItemsInput }): string {
  return `
import type { LayoutLoad } from "./$types.ts";
import type { NavItemsInput } from "$lib/models/docs.ts";

export const load: LayoutLoad = (): { navItems: NavItemsInput } => (${JSON.stringify(data)});
`;
}

function indexPageContent(data: ArticleInput & { title: string }): string {
  return `
import type { ArticleInput } from "$lib/models/docs.ts";
import type { PageLoad } from "./$types.ts";

export const load: PageLoad = (): ArticleInput & { title: string } => (${JSON.stringify(data)});
`;
}

function replaceCodeLang(source: string): string {
  return source.replaceAll(
    /```\{(?<content>[^}]+)\}/g,
    (_match, content: string): string => {
      let result = /^\s*\.(?<lang>[-a-zA-Z]+)/.exec(content);
      let lang = result?.groups?.["lang"];
      if (!lang) {
        throw new Error(`Can't find code block lang: ${source}`);
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
