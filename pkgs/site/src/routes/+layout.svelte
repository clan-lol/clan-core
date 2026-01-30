<script lang="ts">
  import "./global.css";
  import type {
    Pagefind,
    PagefindSearchFragment,
  } from "vite-plugin-pagefind/types";
  import config from "~/config/index.js";
  import favicon from "$lib/assets/favicon.svg";
  import type { NavItem, Path } from "$lib/models/docs/index.ts";
  import { onMount } from "svelte";
  import { onNavigate } from "$app/navigation";
  import { resolve } from "$app/paths";

  const { data, children } = $props();
  const docs = $derived(data.docs);
  let menuOpen = $state(false);
  let pagefind: Pagefind | undefined;
  let query = $state("");
  let searchResults: PagefindSearchFragment[] = $state([]);

  onMount(async () => {
    const pf = (await import(
      /* @vite-ignore */ resolve("/pagefind/pagefind.js")
    )) as Pagefind;
    await pf.init();
    pagefind = pf;
  });
  onNavigate(() => {
    menuOpen = false;
    query = "";
    document.documentElement.classList.remove("no-scroll");
  });
  $effect(() => {
    (async (): Promise<void> => {
      if (!pagefind) {
        return;
      }
      const search = await pagefind.debouncedSearch(query);
      searchResults = await Promise.all(
        search.results
          .slice(0, config.searchResultLimit)
          .map(async (r) => await r.data()),
      );
    })();
  });

  function toggleMenu(): void {
    menuOpen = !menuOpen;
    window.scrollTo({ top: 0 });
    document.documentElement.classList.toggle("no-scroll", menuOpen);
  }
</script>

<svelte:head>
  <link href={favicon} rel="icon" />
</svelte:head>

<div class="global-bar">
  <span>Clan Docs</span>
  <nav>
    <div class="search">
      <input type="search" bind:value={query} />
      {#if searchResults.length > 0}
        <ul>
          {#each searchResults as searchResult (searchResult.excerpt)}
            <li class="search-result">
              <div class="search-result-title">
                <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
                <a
                  href={resolve(
                    searchResult.url.slice(0, -".html".length) as Path,
                  )}>{searchResult.meta["title"]}</a
                >
              </div>
              <div class="search-result-excerpt">
                <!-- eslint-disable-next-line svelte/no-at-html-tags -->
                {@html searchResult.excerpt}
              </div>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
    <div class={["menu", menuOpen && "open"]}>
      <button onclick={toggleMenu} type="button">Menu</button>
      <ul>
        {@render navItems(docs.navItems)}
      </ul>
    </div>
  </nav>
</div>
<main>
  {@render children?.()}
</main>

{#snippet navItems(items: readonly NavItem[])}
  {#each items as item (item.label)}
    {@render navItem(item)}
  {/each}
{/snippet}

{#snippet navItem(item: NavItem)}
  {#if "items" in item}
    <li>
      <details open={!item.collapsed}>
        <summary><span>{item.label}</span></summary>
        <ul>
          {@render navItems(item.items)}
        </ul>
      </details>
    </li>
  {:else}
    <li>
      <a href={resolve(item.link)}>{item.label}</a>
    </li>
  {/if}
{/snippet}

<style>
  .global-bar {
    height: var(--globalBarHeight);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 var(--pageMargin);
    color: var(--fgInvertedColor);
    background: var(--bgInvertedColor);
  }
  .search {
    & > ul {
      position: fixed;
      z-index: 10;
      left: 0;
      top: var(--globalBarHeight);
      width: 100vw;
      height: 100vh;
      background: #fff;
    }
  }
  .search-result {
    padding: 15px;
    border-bottom: 1px solid #a3a3a3;
  }
  .search-result-title {
    padding: 0 0 15px;
  }
  .search-result-excerpt {
    color: #666;
  }
  .menu {
    color: var(--fgColor);
    & > ul {
      visibility: hidden;
      position: fixed;
      left: 0;
      z-index: 10;
      top: var(--globalBarHeight);
      width: 100vw;
      height: 100vh;
      background: #fff;
    }
    &.open > ul {
      visibility: visible;
    }
    li {
      padding-left: 1em;
    }
  }

  nav {
    display: flex;
    align-items: center;
  }
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
</style>
