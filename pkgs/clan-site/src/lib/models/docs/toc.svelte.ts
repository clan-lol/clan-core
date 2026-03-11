import type { Action } from "svelte/action";
import type { Docs } from "./docs.svelte.ts";
import type { TocItemInput, TocItemsInput } from "./toc.ts";
import { viewport } from "../viewport.ts";
import { visit } from "$lib/util.ts";

export class Toc {
  public readonly setContent: Action = this.#setContent.bind(this);
  public readonly setHeight: Action = this.#setHeight.bind(this);
  public readonly onClickTitle = this.#onClickTitle.bind(this);
  public readonly docs: Docs;
  public open = $state(false);
  public items: TocItems;
  #activeTocItem: TocItem | undefined = $state();
  public get activeTocItem(): TocItem | undefined {
    return this.#activeTocItem;
  }
  #content: HTMLElement | undefined;
  #height = $state(0);
  #observer: IntersectionObserver | undefined;

  public constructor(tocItems: () => TocItemsInput, docs: Docs) {
    this.items = $derived(new TocItems(tocItems(), this));
    this.docs = docs;

    $effect(() => {
      // Make sure items update trigger this function
      this.items;
      this.#updateTocItemOnScrollHeading();
      return (): void => this.reset();
    });
  }

  public reset(): void {
    this.#observer?.disconnect();
    this.#observer = undefined;
    this.#activeTocItem = undefined;
    this.open = false;
  }

  public toggleExpanded(): boolean {
    this.open = !this.open;
    return this.open;
  }

  #onClickTitle(ev: Event): void {
    ev.preventDefault();

    if (viewport.isWide) {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } else {
      this.toggleExpanded();
    }
  }

  #setContent(node: HTMLElement): void {
    this.#content = node;
  }

  #setHeight(node: HTMLElement): void {
    this.#height = node.offsetHeight;
  }

  #updateTocItemOnScrollHeading(): void {
    if (viewport.isWide || !this.#content || this.#height === 0) {
      return;
    }
    this.#observer = new IntersectionObserver(
      (entries) => this.#updateTocItem(entries),
      {
        threshold: 1,
        rootMargin: `${-this.#height}px 0px 0px`,
      },
    );
    for (const heading of this.#content.querySelectorAll("h1,h2,h3,h4,h5,h6")) {
      this.#observer.observe(heading);
    }
  }
  #updateTocItem(entries: IntersectionObserverEntry[]): void {
    for (const entry of entries) {
      visit(this.items, (tocItem) => {
        if (tocItem.id !== entry.target.id || !entry.rootBounds) {
          return;
        }
        tocItem.scrolledPast =
          entry.intersectionRatio < 1 &&
          entry.boundingClientRect.top < entry.rootBounds.top
            ? entry.rootBounds.top - entry.boundingClientRect.top
            : 0;
      });
    }
    // Find the last heading with scrolledPast > 0
    let active: TocItem | undefined;
    visit(this.items, (tocItem) => {
      if (tocItem.scrolledPast === 0) {
        return "break";
      }
      active = tocItem;
      return;
    });

    this.#activeTocItem = active;
  }
}

export class TocItems extends Array<TocItem> {
  public constructor(items: TocItemsInput, toc: Toc) {
    super(...items.map((item) => new TocItem(item, toc)));
  }
}
export class TocItem {
  public readonly id: string;
  public readonly label: string;
  public readonly children: TocItems;
  public readonly onClick = this.#onClick.bind(this);
  public scrolledPast: number;
  #toc: Toc;

  public constructor(input: TocItemInput, toc: Toc) {
    this.id = input.id;
    this.label = input.label;
    this.scrolledPast = 0;
    this.children = new TocItems(input.children, toc);
    this.#toc = toc;
  }

  #onClick(ev: Event): void {
    ev.preventDefault();
    if (!viewport.isWide) {
      this.#toc.open = false;
    }
    // eslint-disable-next-line unicorn/prefer-query-selector
    const heading = document.getElementById(this.id);
    if (!heading) {
      return;
    }
    heading.scrollIntoView({
      behavior: "smooth",
    });
    globalThis.history.pushState(undefined, "", `#${this.id}`);
  }
}
