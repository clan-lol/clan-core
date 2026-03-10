import type { Docs } from "../docs.ts";
import type {
  Pagefind,
  PagefindSearchFragment,
} from "@clan.lol/vite-plugin-pagefind";
import { asset } from "$app/paths";
import { browser } from "$app/environment";
import { searchResultLimit } from "$config";

export class Search {
  #docs: Docs;
  public query = $state("");
  public inputElement: HTMLInputElement | undefined = $state.raw();
  public fakeInputElement: HTMLInputElement | undefined = $state.raw();
  #results: readonly PagefindSearchFragment[] = $state.raw([]);
  public get results(): readonly PagefindSearchFragment[] {
    return this.#results;
  }
  #pagefind: Pagefind | undefined = $state.raw();

  public constructor(docs: Docs) {
    this.#docs = docs;

    $effect(() => {
      if (this.#docs.topbarMode === "search") {
        if (this.inputElement && this.fakeInputElement) {
          this.inputElement.style.left = `${String(this.fakeInputElement.offsetLeft)}px`;
          this.inputElement.style.top = `${String(this.fakeInputElement.offsetTop)}px`;
          this.inputElement.style.width = `${String(this.fakeInputElement.offsetWidth)}px`;
          this.inputElement.style.height = `${String(this.fakeInputElement.offsetHeight)}px`;
          this.inputElement.focus();
        }
      } else {
        this.query = "";
        if (this.inputElement) {
          this.inputElement.blur();
        }
      }
    });

    if (browser) {
      (async (): Promise<void> => {
        this.#pagefind = (await import(
          /* @vite-ignore */ asset("/_pagefind/docs/pagefind.js")
        )) as Pagefind;
        await this.#pagefind.init();
        // Override the baseUrl that pagefind derives from import.meta.url.
        // Without this, pagefind derives baseUrl from the asset path
        // (e.g. /_assets/unstable/) and prepends it to result URLs,
        // producing broken links like /_assets/unstable/docs/unstable/...
        await this.#pagefind.options({ baseUrl: "/" });
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
