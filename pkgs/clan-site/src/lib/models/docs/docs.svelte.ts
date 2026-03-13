import type { ArticleInput, DocsPath, TopBarMode } from "./docs.ts";
import type { NavItemsInput, NavSibling } from "./nav.ts";
import { afterNavigate, beforeNavigate } from "$app/navigation";
import CopyButton from "~/lib/components/CopyButton.svelte";
import { createContext, mount } from "svelte";
import { customMedia, docsBase, version } from "$config";
import { HTTP_OK } from "$lib/util.ts";
import { MediaQuery } from "svelte/reactivity";
import { Nav } from "./nav.svelte.ts";
import { resolve } from "$app/paths";
import { Search } from "./search.svelte.ts";
import { Toc } from "./toc.svelte.ts";

export type DocsLayout = "mobile" | "tablet" | "desktop";
export class Docs {
  public static readonly versionedBase: DocsPath = `${docsBase}/${version}`;

  public static async getVersions(): Promise<string[]> {
    const res = await fetch(resolve(`${docsBase}/versions`));
    if (res.status !== HTTP_OK) {
      throw new Error(`Failed to fetch docs version: ${res.statusText}`);
    }
    const s = await res.text();
    return s
      .trim()
      .split("\n")
      .map((v) => v.trim());
  }

  public readonly layout: DocsLayout;
  public readonly isTopBarFixed: boolean;
  public readonly nav: Nav;
  public readonly article: Article;
  public readonly search: Search;
  public topbarMode: TopBarMode = $state("navBar");
  public constructor(navItems: NavItemsInput, article: () => ArticleInput) {
    const tablet = new MediaQuery(customMedia.docsTablet);
    const desktop = new MediaQuery(customMedia.docsDesktop);
    this.layout = $derived.by(() => {
      if (desktop.current) {
        return "desktop";
      }
      if (tablet.current) {
        return "tablet";
      }
      return "mobile";
    });
    const fixedMq = new MediaQuery(customMedia.docsTopBarFixed);
    this.isTopBarFixed = $derived(fixedMq.current);
    this.nav = new Nav(navItems, () => article().navPointer, this);
    this.article = new Article(article, this);
    this.search = new Search(this);

    beforeNavigate((navigation) => {
      if (!navigation.willUnload) {
        this.topbarMode = "navBar";
      }
    });
  }
}

export const [getDocsContext, setDocsContext] = createContext<Docs>();

export class Article {
  public readonly toc: Toc;
  public readonly prev: NavSibling | undefined;
  public readonly next?: NavSibling | undefined;
  public element: HTMLElement | undefined = $state.raw();

  public constructor(article: () => ArticleInput, docs: Docs) {
    this.toc = new Toc(() => article().toc, docs);
    this.prev = $derived(article().prev);
    this.next = $derived(article().next);
    this.#addCodeBlockCopyButtonsOnChangePage();
  }

  #addCodeBlockCopyButtonsOnChangePage(): void {
    const fn = (): void => this.#addCodeBlockCopyButtons();
    $effect(fn);
    afterNavigate(fn);
  }
  #addCodeBlockCopyButtons(): void {
    if (!this.element) {
      return;
    }
    for (const pre of this.element.querySelectorAll("pre.shiki")) {
      mount(CopyButton, {
        target: pre,
      });
    }
  }
}
