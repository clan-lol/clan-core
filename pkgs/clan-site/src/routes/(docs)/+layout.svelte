<script lang="ts">
  import type { NavGroup, NavItem } from "$lib/models/docs.ts";
  import type {
    Pagefind,
    PagefindSearchFragment,
  } from "vite-plugin-pagefind/types";
  import { asset, resolve } from "$app/paths";
  import ClanLogo from "$lib/assets/icons/clan-logo.svg?component";
  import config from "$config";
  import favicon from "$lib/assets/favicon.svg";
  import IconSearch from "$lib/assets/icons/search.svg?component";
  import { onMount } from "svelte";
  import { onNavigate } from "$app/navigation";
  import { page } from "$app/state";
  import "~/base.css";

  const { children } = $props();
  if (!page.data.docs) {
    throw new Error("Missing docs page data");
  }
  const docs = $derived(page.data.docs);
  const activeNavGroup = $derived(
    docs.navItems.find((navItem) => "items" in navItem && navItem.isActive) as
      | NavGroup
      | undefined,
  );
  let pagefind: Pagefind | undefined;
  let query = $state("");
  let searchResults: PagefindSearchFragment[] = $state([]);

  onMount(async () => {
    const pf = (await import(
      /* @vite-ignore */ asset("/pagefind/pagefind.js")
    )) as Pagefind;
    await pf.init();
    pagefind = pf;
  });
  onNavigate(() => {
    query = "";
    window.scrollTo(0, 0);
  });
  $effect(() => {
    (async (): Promise<void> => {
      if (!pagefind) {
        return;
      }
      const search = await pagefind.debouncedSearch(query);
      searchResults = await Promise.all(
        search.results
          .slice(0, config.docs.searchResultLimit)
          .map(async (r) => await r.data()),
      );
    })();
  });
</script>

<svelte:head>
  <link href={favicon} rel="icon" />
  <title>{docs.article.title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    rel="preconnect"
    href="https://fonts.gstatic.com"
    crossorigin="anonymous"
  />
  <link
    href="https://fonts.googleapis.com/css2?family=Mona+Sans:ital,wght@0,200..900;1,200..900&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div class="container">
  <header>
    <div class="logo"><ClanLogo /> Document</div>
    <nav class="nav">
      <ul>
        {#each docs.navItems as navItem (navItem.label)}
          {#if "items" in navItem}
            <li>
              <a href={resolve(`/docs/${config.ver}`)}>{navItem.label}</a>
            </li>
          {:else if "path" in navItem}
            <li><a href={resolve(navItem.path)}>{navItem.label}</a></li>
          {:else}
            <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
            <li><a href={navItem.url}>{navItem.label}</a></li>
          {/if}
        {/each}
      </ul>
    </nav>
  </header>
  <div class="main">
    <aside>
      <div class="search">
        <div class="search-bar">
          <IconSearch height="14" /><input
            type="search"
            placeholder="Search"
            bind:value={query}
          />
        </div>
        {#if searchResults.length !== 0}
          <ul>
            {#each searchResults as searchResult (searchResult.excerpt)}
              <li class="search-result">
                <div class="search-result-title">
                  <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
                  <a href={searchResult.url.slice(0, -".html".length)}
                    >{searchResult.meta["title"]}</a
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
      {#if activeNavGroup}
        <nav class="toc">
          <div class="nav-title">{activeNavGroup.label}</div>
          <ul>
            {@render navItems(activeNavGroup.items)}
          </ul>
        </nav>
      {/if}
    </aside>
    <main>
      {@render children?.()}
    </main>
  </div>
</div>
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
  {:else if "path" in item}
    <li class:active={item.isActive}>
      <a href={resolve(item.path)}>{item.label}</a>
    </li>
  {:else}
    <li>
      <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
      <a href={item.url}>{item.label}</a>
    </li>
  {/if}
{/snippet}

<style>
  :global {
    body {
      color: #000;
      font:
        500 18px/1.37 "Mona Sans",
        sans-serif;
      background: #e1ecf0;
    }

    a {
      text-decoration: none;
    }
    h1 {
      font-size: 40px;
      font-weight: 700px;
      color: inherit;
    }

    h2 {
      font-size: inherit;
      font-weight: inherit;
      color: #415e63;
    }
  }
  .container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    border-top: 1px solid #c9d7d9;
  }

  .nav {
    > ul {
      list-style: none;
      display: flex;
      margin: 0;
      margin-right: -8px;
      padding: 0;
      a {
        display: block;
        font-size: 14px;
        color: inherit;
        padding: 24px 16px;
      }
    }
  }
  .logo {
    display: flex;
    gap: 10px;
    align-items: center;
    font-weight: bold;
    font-size: 20px;

    :global(svg) {
      height: 28px;
    }
  }
  .main {
    display: flex;
    flex: 1;
  }
  aside {
    width: 260px;
    padding: 0 24px;
    flex: none;
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
  .search-bar {
    border-radius: 2px;
    border: #7b9b9f;
    background: #fff;
    font-size: 14px;
    padding: 6px 8px;
    margin: 24px 0;
    display: flex;
    align-items: center;
    gap: 7px;

    & > input {
      flex: 1;
      border: none;
      outline: none;
      padding: 0;
      font: inherit;
      font-size: 14px;

      &::placeholder {
        color: #4f747a;
      }
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

  .nav-title {
    text-transform: uppercase;
    font-size: 12px;
    color: #415e63;
    font-weight: 600;
  }
  .toc ul {
    list-style: none;
    padding: 0;
    margin: 0;
    margin-top: 12px;

    > li {
      border-radius: 6px;
      &.active {
        background-color: #fff;
      }
      a {
        display: block;
        color: inherit;
        font-size: 14px;
        line-height: 1.25;
        padding: 8px 12px;
      }
    }
  }
  main {
    flex: 1;
    background: #fff;
    margin-right: 24px;
    margin-bottom: 24px;
    border-radius: 12px;
  }
</style>
