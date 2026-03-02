import type { ArticleInput, MastheadMode } from "./docs.ts";
import type { NavItemsInput, NavSibling } from "./nav.ts";
import { createContext } from "svelte";
import { customMedia } from "$config";
import { MediaQuery } from "svelte/reactivity";
import { Nav } from "./nav.svelte.ts";
import { Toc } from "./toc.svelte.ts";

export class Docs {
  public readonly nav: Nav;
  public readonly article: Article;
  public readonly isWide: boolean;
  public mastheadMode: MastheadMode = $state(false);
  public constructor(navItems: NavItemsInput, article: () => ArticleInput) {
    const wide = new MediaQuery(customMedia.wide.slice(1, -1));
    this.isWide = $derived(wide.current);
    this.nav = new Nav(navItems, () => article().navPointer, this);
    this.article = new Article(article, this);
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
