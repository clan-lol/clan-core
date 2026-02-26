import type { Action } from "svelte/action";
import type {
  Article,
  TocItem as TocItemInput,
  TocItems as TocItemsInput,
} from "$lib/models/docs.ts";
import type { Page } from "@sveltejs/kit";
import { beforeNavigate } from "$app/navigation";
import { customMedia } from "$config";
import { MediaQuery } from "svelte/reactivity";
import { visit } from "$lib/util.ts";

export class Toc {
  public readonly tocItems: TocItems;
  public readonly isWide: boolean;
  public readonly setHeadings: Action = this.#setHeadings.bind(this);
  public readonly setHeight: Action = this.#setHeight.bind(this);
  public readonly onClickTitle = this.#onClickTitle.bind(this);
  public isExpanded = $state(false);
  #activeTocItem: TocItem | undefined = $state();
  public get activeTocItem(): TocItem | undefined {
    return this.#activeTocItem;
  }
  #height = $state(0);
  #headings: HTMLElement[] = $state.raw([]);
  #observer: IntersectionObserver | undefined;

  public constructor(page: Page) {
    this.tocItems = $derived(new TocItems((page.data as Article).toc, this));
    const wide = new MediaQuery(customMedia.wide.slice(1, -1));
    this.isWide = $derived(wide.current);

    $effect(() => {
      if (!this.isWide && this.#headings.length !== 0 && this.#height !== 0) {
        this.#updateTocItemOnScrollHeading();
      }
      return () => this.reset();
    });

    beforeNavigate(() => {
      this.isExpanded = false;
    });
  }

  public reset(): void {
    this.#observer?.disconnect();
    this.#observer = undefined;
    this.#activeTocItem = undefined;
    this.isExpanded = false;
  }

  public toggleExpanded(): boolean {
    this.isExpanded = !this.isExpanded;
    return this.isExpanded;
  }

  #onClickTitle(ev: Event): void {
    ev.preventDefault();

    if (this.isWide) {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } else {
      this.toggleExpanded();
    }
  }

  #setHeadings(node: HTMLElement): void {
    this.#headings = [
      ...node.querySelectorAll("h1,h2,h3,h4,h5,h6"),
    ] as HTMLElement[];
  }

  #setHeight(node: HTMLElement): void {
    this.#height = node.offsetHeight;
  }

  #updateTocItemOnScrollHeading(): void {
    this.#observer = new IntersectionObserver(
      (entries) => this.#updateTocItem(entries),
      {
        threshold: 1,
        rootMargin: `${(-this.#height).toFixed(0)}px 0px 0px`,
      },
    );
    for (const heading of this.#headings) {
      this.#observer.observe(heading);
    }
  }
  #updateTocItem(entries: IntersectionObserverEntry[]): void {
    for (const entry of entries) {
      visit(this.tocItems, (tocItem) => {
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
    let last: TocItem | undefined;
    let active: TocItem | undefined;
    visit(this.tocItems, (tocItem) => {
      if (last && last.scrolledPast > 0 && tocItem.scrolledPast === 0) {
        active = last;
        return "break";
      }
      last = tocItem;
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
    if (!this.#toc.isWide) {
      this.#toc.isExpanded = false;
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
