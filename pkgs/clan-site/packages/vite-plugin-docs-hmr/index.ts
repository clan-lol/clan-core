import type { Output } from "@clan.lol/svelte-md";
import type { PluginOption, ViteDevServer } from "vite";
import { availableParallelism } from "node:os";
import { mkdir, opendir, readFile, rm, writeFile } from "node:fs/promises";
import pathutil from "node:path";
import { render } from "@clan.lol/svelte-md";

async function mapParallel<T>(
  items: Iterable<T>,
  limit: number,
  fn: (item: T) => Promise<void>,
): Promise<void> {
  const iter = items[Symbol.iterator]();
  async function worker(): Promise<void> {
    for (;;) {
      const result: IteratorResult<T> = iter.next();
      if (result.done === true) {
        return;
      }
      // eslint-disable-next-line no-await-in-loop -- intentional serial processing per worker
      await fn(result.value);
    }
  }
  await Promise.all(
    Array.from({ length: limit }, async () => {
      await worker();
    }),
  );
}

const PARALLELISM = Math.max(1, availableParallelism() - 1);

export type NavItemsInput<P extends string = string> =
  readonly NavItemInput<P>[];
export type NavItemInput<P extends string = string> =
  | { label: string; path: P }
  | { label: string; url: string }
  | { label: string; open: boolean; children: NavItemsInput<P> };
export type NavPointer = readonly number[];
export interface NavSibling<P extends string = string> {
  label: string;
  path: P;
}

export interface ArticleInput<P extends string = string> {
  toc: readonly unknown[];
  navPointer: NavPointer;
  prev?: NavSibling<P>;
  next?: NavSibling<P>;
}

export interface RenderOptions {
  readonly codeLightTheme: string;
  readonly codeDarkTheme: string;
  readonly minLineNumberLines: number;
  readonly maxTocDepth: number;
  readonly componentsSpecifierPrefix?: string;
}

export interface NavHelpers<P extends string = string> {
  readonly getItems: (
    titles: Readonly<Record<string, string>>,
  ) => Promise<NavItemsInput<P>>;
  readonly findSiblings: (
    navItems: NavItemsInput<P>,
    path: string,
  ) => readonly [NavSibling<P> | undefined, NavSibling<P> | undefined];
  readonly getPointer: (navItems: NavItemsInput<P>, path: string) => NavPointer;
}

export interface DocsOptions<P extends string = string> {
  readonly srcDir: string;
  readonly embedsDir: string;
  readonly articlesDir: string;
  readonly layoutDir: string;
  readonly render: RenderOptions;
  readonly nav: NavHelpers<P>;
}

export type DocsHmrOptions<P extends string = string> = DocsOptions<P>;

export interface PrerenderDocsOptions<
  P extends string = string,
> extends DocsOptions<P> {
  readonly root: string;
}

function componentsPrefix(render: RenderOptions): string {
  return render.componentsSpecifierPrefix ?? "$lib/components";
}

async function readIndexArticleTitle(articlesDir: string): Promise<string> {
  const path = pathutil.join(articlesDir, "+page.svelte");
  const content = await readFile(path, { encoding: "utf8" });
  const result = /<h1[^>]*>(?<title>.+?)<\/h1>/s.exec(content);
  const title = result?.groups?.["title"];
  if (!title) {
    throw new Error(`Missing <h1> title in ${path}`);
  }
  return title;
}

export function replaceCodeLang(source: string, filename: string): string {
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

export function replaceButtonSyntax(source: string): string {
  return source.replaceAll(
    /\[(?<title>[^\]]+)\]\((?<url>[^)]+)\)\{(?<html>[^}]+)\}/g,
    (_match, title: string, url: string) => `[${title}](${url})`,
  );
}

export async function loadOutput(
  filename: string,
  renderRoot: string,
  options: Pick<DocsOptions, "embedsDir" | "render">,
): Promise<Output> {
  let source = await readFile(filename, { encoding: "utf8" });
  source = source.replaceAll("```shellSession", "```console");
  source = source.replaceAll("'/dev/sd<X>'", "`/dev/sd<X>`");
  source = source.replaceAll(
    /<div\sclass="grid cards"\smarkdown>(?<md>.+?)<\/div>/gs,
    "$1",
  );
  source = replaceCodeLang(source, filename);
  source = replaceButtonSyntax(source);
  return await render(source, {
    root: renderRoot,
    filename,
    codeLightTheme: options.render.codeLightTheme,
    codeDarkTheme: options.render.codeDarkTheme,
    minLineNumberLines: options.render.minLineNumberLines,
    maxTocDepth: options.render.maxTocDepth,
    codeEmbedDir: options.embedsDir,
  });
}

export function pageContent(data: ArticleInput): string {
  return `
import type { Article } from "$lib/models/docs.ts";
import type { PageLoad } from "./$types.ts";

export const load: PageLoad = (): Article => (${JSON.stringify(data)});
`;
}

export function pageSvelteContent(output: Output, prefix: string): string {
  const imports = [...output.svelteComponents]
    .map(
      (name) =>
        `  import ${name} from ${JSON.stringify(`${prefix}/${name}.svelte`)}`,
    )
    .join(";\n");
  return `
<script lang="ts">
${imports}
</script>
<svelte:head>
  <title>{${JSON.stringify(output.title)}}</title>
</svelte:head>
${output.markup}
`;
}

export function layoutContent(data: { navItems: NavItemsInput }): string {
  return `
import type { LayoutLoad } from "./$types.ts";
import type { NavItemsInput } from "$lib/models/docs.ts";

export const load: LayoutLoad = (): { navItems: NavItemsInput } => (${JSON.stringify(data)});
`;
}

export function indexPageContent(
  data: ArticleInput & { title: string },
): string {
  return `
import type { ArticleInput } from "$lib/models/docs.ts";
import type { PageLoad } from "./$types.ts";

export const load: PageLoad = (): ArticleInput & { title: string } => (${JSON.stringify(data)});
`;
}

export async function discoverFiles(
  rootDir: string,
): Promise<Map<string, string>> {
  const pathsByFile = new Map<string, string>();
  for await (const dirent of await opendir(rootDir, { recursive: true })) {
    if (!dirent.isFile() || !dirent.name.endsWith(".md")) {
      continue;
    }
    const filename = pathutil.join(dirent.parentPath, dirent.name);
    const base = pathutil.relative(rootDir, dirent.parentPath);
    const name = dirent.name.slice(0, -".md".length);
    const routePath = pathutil.join(base, name === "index" ? "" : name);
    pathsByFile.set(filename, routePath);
  }
  return pathsByFile;
}

export async function writeArticle<P extends string = string>(
  routePath: string,
  output: Output,
  navItems: NavItemsInput<P>,
  articlesDir: string,
  options: DocsOptions<P>,
): Promise<void> {
  const [prev, next] = options.nav.findSiblings(navItems, routePath);
  const navPointer = options.nav.getPointer(navItems, routePath);
  const prefix = componentsPrefix(options.render);

  const dir = pathutil.join(articlesDir, routePath);
  await mkdir(dir, { recursive: true });
  await Promise.all([
    writeFile(
      pathutil.join(dir, "+page.ts"),
      pageContent({
        toc:
          (output.frontmatter as Record<string, unknown>)["toc"] === false
            ? []
            : output.toc,
        navPointer,
        ...(prev ? { prev } : {}),
        ...(next ? { next } : {}),
      }),
    ),
    writeFile(
      pathutil.join(dir, "+page.svelte"),
      pageSvelteContent(output, prefix),
    ),
  ]);
}

export async function writeIndexArticle<P extends string = string>(
  navItems: NavItemsInput<P>,
  indexTitle: string,
  articlesDir: string,
  options: DocsOptions<P>,
): Promise<void> {
  const [prev, next] = options.nav.findSiblings(navItems, "");
  const navPointer = options.nav.getPointer(navItems, "");
  await writeFile(
    pathutil.join(articlesDir, "+page.ts"),
    indexPageContent({
      title: indexTitle,
      toc: [],
      navPointer,
      ...(prev ? { prev } : {}),
      ...(next ? { next } : {}),
    }),
  );
}

export async function prerenderDocs<P extends string = string>(
  options: PrerenderDocsOptions<P>,
): Promise<void> {
  const rootDir = pathutil.resolve(options.root, options.srcDir);
  const articlesDir = pathutil.resolve(options.root, options.articlesDir);
  const layoutDir = pathutil.resolve(options.root, options.layoutDir);
  const renderRoot = pathutil.dirname(options.root);

  const pathsByFile = await discoverFiles(rootDir);

  const outputs = new Map<string, Output>();
  const titles: Record<string, string> = {};
  await mapParallel(
    pathsByFile.entries(),
    PARALLELISM,
    async ([filename, routePath]) => {
      const output = await loadOutput(filename, renderRoot, options);
      outputs.set(routePath, output);
      titles[routePath] = output.title;
    },
  );

  const indexTitle = await readIndexArticleTitle(articlesDir);
  titles[""] = indexTitle;
  const navItems = await options.nav.getItems(titles);

  await Promise.all([
    ...[...outputs.entries()].map(async ([routePath, output]) => {
      await writeArticle(routePath, output, navItems, articlesDir, options);
    }),
    writeIndexArticle(navItems, indexTitle, articlesDir, options),
    writeFile(
      pathutil.join(layoutDir, "+layout.ts"),
      layoutContent({ navItems }),
    ),
  ]);
}

export default function vitePluginDocsHmr<P extends string = string>(
  options: DocsHmrOptions<P>,
): PluginOption {
  let pathsByFile: Map<string, string>;
  let outputs: Map<string, Output>;
  let titles: Map<string, string>;
  let viteRoot: string;
  let renderRoot: string;

  async function rebuildFile(
    filename: string,
    rootDir: string,
    articlesDir: string,
    layoutDir: string,
    server: ViteDevServer,
  ): Promise<void> {
    const existing = pathsByFile.get(filename);
    const isNewFile = existing === undefined;

    let routePath: string;
    if (isNewFile) {
      const base = pathutil.relative(rootDir, pathutil.dirname(filename));
      const name = pathutil.basename(filename, ".md");
      routePath = pathutil.join(base, name === "index" ? "" : name);
      pathsByFile.set(filename, routePath);
    } else {
      routePath = existing;
    }

    const output = await loadOutput(filename, renderRoot, options);
    outputs.set(routePath, output);

    const oldTitle = titles.get(routePath);
    titles.set(routePath, output.title);

    const titleChanged = oldTitle !== output.title || isNewFile;

    if (titleChanged) {
      const indexTitle = await readIndexArticleTitle(articlesDir);
      titles.set("", indexTitle);
      const titlesObj = Object.fromEntries(titles);
      const navItems = await options.nav.getItems(titlesObj);

      await Promise.all([
        writeFile(
          pathutil.join(layoutDir, "+layout.ts"),
          layoutContent({ navItems }),
        ),
        ...[...outputs.entries()].map(async ([rp, out]) => {
          await writeArticle(rp, out, navItems, articlesDir, options);
        }),
        writeIndexArticle(navItems, indexTitle, articlesDir, options),
      ]);
    } else {
      const titlesObj = Object.fromEntries(titles);
      const navItems = await options.nav.getItems(titlesObj);
      await writeArticle(routePath, output, navItems, articlesDir, options);
    }

    server.ws.send({ type: "full-reload" });
  }

  async function handleDelete(
    filename: string,
    articlesDir: string,
    layoutDir: string,
    server: ViteDevServer,
  ): Promise<void> {
    const routePath = pathsByFile.get(filename);
    if (routePath === undefined) {
      return;
    }

    pathsByFile.delete(filename);
    outputs.delete(routePath);
    titles.delete(routePath);

    // Remove generated route files from disk so SvelteKit no longer serves
    // the deleted page.
    const routeDir = pathutil.join(articlesDir, routePath);
    await rm(routeDir, { recursive: true, force: true });

    const indexTitle = await readIndexArticleTitle(articlesDir);
    titles.set("", indexTitle);
    const titlesObj = Object.fromEntries(titles);
    const navItems = await options.nav.getItems(titlesObj);

    await Promise.all([
      writeFile(
        pathutil.join(layoutDir, "+layout.ts"),
        layoutContent({ navItems }),
      ),
      ...[...outputs.entries()].map(async ([rp, out]) => {
        await writeArticle(rp, out, navItems, articlesDir, options);
      }),
      writeIndexArticle(navItems, indexTitle, articlesDir, options),
    ]);

    server.ws.send({ type: "full-reload" });
  }

  return {
    name: "@clan.lol/vite-plugin-docs-hmr",
    apply: "serve",
    configResolved(config): void {
      viteRoot = config.root;
      renderRoot = pathutil.dirname(viteRoot);
    },
    configureServer(server): void {
      const rootDir = pathutil.resolve(viteRoot, options.srcDir);
      const articlesDir = pathutil.resolve(viteRoot, options.articlesDir);
      const layoutDirAbs = pathutil.resolve(viteRoot, options.layoutDir);
      const embedsDirAbs = pathutil.resolve(viteRoot, options.embedsDir);

      server.watcher.add([rootDir, embedsDirAbs]);

      async function initialize(): Promise<void> {
        const discovered = await discoverFiles(rootDir);
        pathsByFile = discovered;
        outputs = new Map();
        titles = new Map();
        await mapParallel(
          pathsByFile.entries(),
          PARALLELISM,
          async ([filename, routePath]) => {
            const output = await loadOutput(filename, renderRoot, options);
            outputs.set(routePath, output);
            titles.set(routePath, output.title);
          },
        );
        const indexTitle = await readIndexArticleTitle(articlesDir);
        titles.set("", indexTitle);
        // eslint-disable-next-line no-console -- dev server diagnostic output
        console.log(
          `[docs-hmr] Watching ${pathsByFile.size} markdown files for changes`,
        );
      }

      const initPromise = initialize();

      // Serial queue: prevent interleaved rebuilds when multiple files
      // change at the same time (e.g. git checkout, batch saves).
      let queue: Promise<void> = Promise.resolve();
      function enqueue(fn: () => Promise<void>): void {
        // eslint-disable-next-line promise/prefer-await-to-then -- intentional serial chaining
        queue = queue.then(fn, fn);
      }

      function handleChange(absPath: string): void {
        if (!absPath.endsWith(".md")) {
          return;
        }
        if (!absPath.startsWith(`${rootDir}/`)) {
          return;
        }
        enqueue(async () => {
          await initPromise;
          // eslint-disable-next-line no-console -- dev server diagnostic output
          console.log(
            `[docs-hmr] Rebuilding: ${pathutil.relative(rootDir, absPath)}`,
          );
          try {
            await rebuildFile(
              absPath,
              rootDir,
              articlesDir,
              layoutDirAbs,
              server,
            );
            // eslint-disable-next-line no-console -- dev server diagnostic output
            console.log(`[docs-hmr] Done`);
          } catch (err) {
            console.error(`[docs-hmr] Error rebuilding ${absPath}:`, err);
          }
        });
      }

      function handleUnlink(absPath: string): void {
        if (!absPath.endsWith(".md")) {
          return;
        }
        if (!absPath.startsWith(`${rootDir}/`)) {
          return;
        }
        enqueue(async () => {
          await initPromise;
          // eslint-disable-next-line no-console -- dev server diagnostic output
          console.log(
            `[docs-hmr] File deleted: ${pathutil.relative(rootDir, absPath)}`,
          );
          try {
            await handleDelete(absPath, articlesDir, layoutDirAbs, server);
          } catch (err) {
            console.error(`[docs-hmr] Error handling delete ${absPath}:`, err);
          }
        });
      }

      server.watcher.on("change", handleChange);
      server.watcher.on("add", handleChange);
      server.watcher.on("unlink", handleUnlink);
    },
  };
}
