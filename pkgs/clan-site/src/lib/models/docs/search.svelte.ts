import type { Docs } from "../docs.ts";
import type {
  Pagefind,
  PagefindSearchFragment,
} from "@clan.lol/vite-plugin-pagefind";
import { asset } from "$app/paths";
import { browser } from "$app/environment";
import { searchResultLimit } from "$config";
import { untrack } from "svelte";

export class Search {
  #docs: Docs;
  public query = $state("");
  public inputElement: HTMLInputElement | undefined = $state.raw();
  public inputDoubleElement: HTMLInputElement | undefined = $state.raw();
  public get inputEffectiveElement(): HTMLInputElement | undefined {
    if (this.#docs.layout === "mobile") {
      return this.inputDoubleElement;
    }
    return this.inputElement;
  }
  #results: readonly PagefindSearchFragment[] = $state.raw([]);
  public get results(): readonly PagefindSearchFragment[] {
    if (this.#docs.topbarMode !== "search") {
      return [];
    }
    return this.#results;
  }
  #pagefind: Pagefind | undefined = $state.raw();

  public constructor(docs: Docs) {
    this.#docs = docs;

    $effect(() => {
      let el: HTMLInputElement | undefined;
      // We don't want viewport change to retrigger this effect
      untrack(() => {
        el = this.inputEffectiveElement;
      });
      if (this.#docs.topbarMode === "search") {
        el?.focus();
      } else {
        el?.blur();
      }
    });

    if (browser) {
      (async (): Promise<void> => {
        this.#pagefind = (await import(
          /* @vite-ignore */ asset("/_pagefind/docs/pagefind.js")
        )) as Pagefind;
        // Override the baseUrl that pagefind derives from import.meta.url.
        // Without this, pagefind derives baseUrl from the asset path
        // (e.g. /_assets/unstable/) and prepends it to result URLs,
        // producing broken links like /_assets/unstable/docs/unstable/...
        await this.#pagefind.options({ baseUrl: "/" });
        await this.#pagefind.init();
      })();
    }

    $effect(() => {
      (async (): Promise<void> => {
        if (!this.query || !this.#pagefind) {
          this.#results = [];
          return;
        }

        const search = await this.#pagefind.debouncedSearch(this.query);
        if (!search) {
          return;
        }

        this.#results = await Promise.all(
          search.results
            .slice(0, searchResultLimit)
            .map(async (r) => await r.data()),
        );
        // By the time excerpts return, user might have already cleared the
        // query, in which case we should throw away the results. Unfortunately
        // pagefind doesn't provide a cancelling API, otherwise we should call
        // it whenever query becomes empty
        if (!this.query) {
          this.#results = [];
        }
      })();
    });
  }
}
