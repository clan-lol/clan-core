import type { Docs } from "./docs.svelte.ts";
import type { TocItemInput, TocItemsInput } from "./toc.ts";
import { browser } from "$app/environment";
import { visit } from "$lib/util.ts";

export class Toc {
  public readonly onClickTitle = this.#onClickTitle.bind(this);
  public readonly docs: Docs;
  public open = $state(false);
  public element: HTMLElement | undefined = $state.raw();
  public items: TocItems;
  #activeTocItem: TocItem | undefined = $state();
  public get activeTocItem(): TocItem | undefined {
    return this.#activeTocItem;
  }
  #observer: IntersectionObserver | undefined;

  public constructor(tocItems: () => TocItemsInput, docs: Docs) {
    this.items = $derived(new TocItems(tocItems(), this));
    this.docs = docs;

    $effect(() => {
      // If items have changed, it means the page has been re-rendered, and we
      // need to restart IntersectionObserver
      this.items;
      this.#updateTocItemOnScrollHeading();
      return (): void => this.reset();
    });

    if (browser) {
      window.addEventListener("resize", () => {
        this.reset();
        this.#updateTocItemOnScrollHeading();
      });
    }
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

    if (this.docs.layout === "desktop") {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } else {
      this.toggleExpanded();
    }
  }

  #updateTocItemOnScrollHeading(): void {
    if (!this.docs.article.element || !this.element) {
      return;
    }
    let offset: number;

    if (this.docs.layout === "desktop") {
      const rect = this.docs.article.element.getBoundingClientRect();
      offset = rect.top + window.scrollY;
    } else {
      const rect = this.element.getBoundingClientRect();
      offset = rect.height + rect.top;
    }
    this.#observer = new IntersectionObserver(
      (entries) => this.#updateTocItem(entries),
      {
        threshold: 1,
        rootMargin: `${-offset}px 0px 0px`,
      },
    );
    for (const heading of this.docs.article.element.querySelectorAll(
      "h1,h2,h3,h4,h5,h6",
    )) {
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
    if (this.#toc.docs.layout !== "desktop") {
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
