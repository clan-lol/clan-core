import type { Docs } from "../docs.ts";
import type {
  Pagefind,
  PagefindSearchFragment,
} from "@clan.lol/vite-plugin-pagefind";
import { asset } from "$app/paths";
import { browser } from "$app/environment";
import { onNavigate } from "$app/navigation";

export class Search {
  #docs: Docs;
  public query = $state("");
  public inputElement: HTMLInputElement | undefined = $state.raw();
  #results: readonly PagefindSearchFragment[] = $state.raw([]);
  public get results(): readonly PagefindSearchFragment[] {
    return this.#results;
  }
  #pagefind: Pagefind | undefined = $state.raw();

  public constructor(docs: Docs) {
    this.#docs = docs;

    onNavigate(() => {
      this.query = "";
    });

    $effect(() => {
      if (this.#docs.topbarMode === "search") {
        if (this.inputElement) {
          this.inputElement.focus();
        }
      } else {
        this.query = "";
      }
    });

    if (browser) {
      (async (): Promise<void> => {
        this.#pagefind = (await import(
          /* @vite-ignore */ asset("/_pagefind/docs/pagefind.js")
        )) as Pagefind;
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
          search.results.map(async (r) => await r.data()),
        );
      })();
    });
  }
}
