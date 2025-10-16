<script lang="ts">
  import favicon from "$lib/assets/favicon.svg";
  import type { NavItem } from "$lib";
  import { onNavigate } from "$app/navigation";
  import { onMount } from "svelte";
  import type {
    Pagefind,
    PagefindSearchFragment,
  } from "vite-plugin-pagefind/types";
  import "./global.css";

  const { data, children } = $props();
  const docs = $derived(data.docs);
  let menuOpen = $state(false);
  onNavigate(() => {
    menuOpen = false;
    query = "";
    document.documentElement.classList.remove("no-scroll");
  });
  let pagefind: Pagefind | undefined;
  let query = $state("");
  let searchResults: PagefindSearchFragment[] = $state([]);
  onMount(async () => {
    // @ts-expect-error
    pagefind = await import("/pagefind/pagefind.js");
    pagefind!.init();
  });
  $effect(() => {
    (async () => {
      query;
      const search = await pagefind?.debouncedSearch(query);
      if (search) {
        searchResults = await Promise.all(
          search.results.slice(0, 5).map((r) => r.data()),
        );
      }
    })();
  });

  function toggleMenu() {
    menuOpen = !menuOpen;
    window.scrollTo({ top: 0 });
    document.documentElement.classList.toggle("no-scroll", menuOpen);
  }
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<div class="global-bar">
  <span class="logo">Clan Docs</span>
  <nav>
    <div class="search">
      <input type="search" bind:value={query} />
      {#if searchResults.length > 0}
        <ul>
          {#each searchResults as searchResult}
            <li class="search-result">
              <div class="search-result-title">
                <a href={searchResult.url.slice(0, -".html".length)}
                  >{searchResult.meta.title}</a
                >
              </div>
              <div class="search-result-excerpt">
                {@html searchResult.excerpt}
              </div>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
    <div class={["menu", menuOpen && "open"]}>
      <button onclick={toggleMenu}>Menu</button>
      <ul>
        {@render navItems(docs.navItems)}
      </ul>
    </div>
  </nav>
</div>
<main>
  {@render children?.()}
</main>

{#snippet navItems(items: NavItem[])}
  {#each items as item}
    {@render navItem(item)}
  {/each}
{/snippet}

{#snippet navItem(item: NavItem)}
  {#if "items" in item}
    <li>
      <details open={!item.collapsed}>
        <summary><span class="label group">{item.label}</span></summary>
        <ul>
          {@render navItems(item.items)}
        </ul>
      </details>
    </li>
  {:else}
    <li>
      <a href={item.link}>{item.label}</a>
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
