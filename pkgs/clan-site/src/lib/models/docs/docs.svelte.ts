import type { ArticleInput, TopBarMode } from "./docs.ts";
import type { NavItemsInput, NavSibling } from "./nav.ts";
import { afterNavigate, beforeNavigate } from "$app/navigation";
import CopyButton from "~/lib/components/CopyButton.svelte";
import { createContext, mount } from "svelte";
import { Nav } from "./nav.svelte.ts";
import { Search } from "./search.svelte.ts";
import { Toc } from "./toc.svelte.ts";

export class Docs {
  public readonly nav: Nav;
  public readonly article: Article;
  public readonly search: Search;
  public topbarMode: TopBarMode = $state("navBar");
  public contentElement: HTMLElement | undefined = $state.raw();
  public constructor(navItems: NavItemsInput, article: () => ArticleInput) {
    this.nav = new Nav(navItems, () => article().navPointer, this);
    this.article = new Article(article, this);
    this.search = new Search(this);
    this.#addCodeBlockCopyButtonsOnChangePage();

    beforeNavigate((navigation) => {
      if (!navigation.willUnload) {
        this.topbarMode = "navBar";
      }
    });
  }

  #addCodeBlockCopyButtonsOnChangePage(): void {
    const fn = (): void => this.#addCodeBlockCopyButtons();
    $effect(fn);
    afterNavigate(fn);
  }
  #addCodeBlockCopyButtons(): void {
    if (!this.contentElement) {
      return;
    }
    for (const pre of this.contentElement.querySelectorAll("pre.shiki")) {
      mount(CopyButton, {
        target: pre,
      });
    }
  }
}

export const [getDocsContext, setDocsContext] = createContext<Docs>();

export class Article {
  public readonly toc: Toc;
  public readonly prev: NavSibling | undefined;
  public readonly next?: NavSibling | undefined;

  public constructor(article: () => ArticleInput, docs: Docs) {
    this.toc = new Toc(() => article().toc, docs);
    this.prev = $derived(article().prev);
    this.next = $derived(article().next);
  }
}
