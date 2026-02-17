<script lang="ts">
  import type {
    Pagefind,
    PagefindSearchFragment,
  } from "@clan/vite-plugin-pagefind";
  import { asset } from "$app/paths";
  import { onMount } from "svelte";
  import { onNavigate } from "$app/navigation";
  import SearchIcon from "$lib/assets/icons/search.svg?component";

  let query = $state("");
  let pagefind: Pagefind | undefined;
  let searchResults: PagefindSearchFragment[] = $state([]);

  onMount(async () => {
    const pf = (await import(
      /* @vite-ignore */ asset("/_pagefind/docs/pagefind.js")
    )) as Pagefind;
    await pf.init();
    pagefind = pf;
  });
  onNavigate(() => {
    query = "";
  });
  $effect(() => {
    (async (): Promise<void> => {
      if (!query || !pagefind) {
        return;
      }
      const search = await pagefind.debouncedSearch(query);
      searchResults = await Promise.all(
        search.results.map(async (r) => await r.data()),
      );
    })();
  });
</script>

<article>
  <header>
    <SearchIcon height="14" /><input
      type="search"
      placeholder="Search"
      bind:value={query}
    />
  </header>
  {#if searchResults.length !== 0}
    <ol>
      {#each searchResults as searchResult (searchResult.excerpt)}
        <li>
          <h2>
            <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
            <a href={searchResult.url.slice(0, -".html".length)}
              >{searchResult.meta["title"]}</a
            >
          </h2>
          <p>
            <!-- eslint-disable-next-line svelte/no-at-html-tags -->
            {@html searchResult.excerpt}
          </p>
        </li>
      {/each}
    </ol>
  {/if}
</article>

<style>
  article {
    display: none;

    & > ul {
      position: fixed;
      inset-inline-start: 0;
      inset-block-start: 0;
      z-index: 10;
      inline-size: 100vw;
      block-size: 100vh;
      background: #fff;
    }
  }

  .search-bar {
    display: flex;
    gap: 7px;
    align-items: center;
    padding: 6px 8px;
    margin: 24px 0;
    background: #fff;
    border: #7b9b9f;
    border-radius: 2px;
    font-size: 14px;

    & > input {
      flex: 1;
      padding: 0;
      border: none;
      outline: none;
      font: inherit;
      font-size: 14px;

      &::placeholder {
        color: #4f747a;
      }
    }
  }

  .search-result {
    padding: 15px;
    border-block-end: 1px solid #a3a3a3;
  }

  .search-result-title {
    padding: 0 0 15px;
  }

  .search-result-excerpt {
    color: #666;
  }
</style>
