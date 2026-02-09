<script lang="ts">
  import type { NavGroup, NavItem } from "~/lib/models/docs.ts";
  import type {
    Pagefind,
    PagefindSearchFragment,
  } from "@clan/vite-plugin-pagefind";
  import { asset, resolve } from "$app/paths";
  import ClanLogo from "$lib/assets/icons/clan-logo.svg?component";
  import config from "$config";
  import favicon from "$lib/assets/favicon.svg";
  import IconSearch from "$lib/assets/icons/search.svg?component";
  import { onMount } from "svelte";
  import { onNavigate } from "$app/navigation";
  import { page } from "$app/state";

  const { data, children } = $props();
  const navItems = $derived(data.docsNavItems);
  const article = $derived(page.data.docsArticle);
  const activeNavGroup = $derived.by(() => {
    const items: { prefixLength: number; group: NavGroup }[] = [];
    for (const navItem of navItems) {
      if (!("items" in navItem)) {
        continue;
      }
      const path = resolve(navItem.path);
      if (!page.url.pathname.startsWith(path)) {
        continue;
      }
      items.push({
        prefixLength: path.length,
        group: navItem,
      });
    }
    items.sort((a, b) => b.prefixLength - a.prefixLength);
    return items[0]?.group;
  });

  let pagefind: Pagefind | undefined;
  let query = $state("");
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
    window.scrollTo(0, 0);
  });
  $effect(() => {
    (async (): Promise<void> => {
      if (!query || !pagefind) {
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
</script>

<svelte:head>
  <link href={favicon} rel="icon" />
  <title>{article?.title || "Clan Documentation"}</title>
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

<div class="container" data-page-id="docs">
  <header>
    <div class="logo"><ClanLogo /> Document</div>
    <nav class="nav">
      <ul>
        {#each navItems as navItem (navItem.label)}
          {#if "path" in navItem}
            <li>
              <a href={resolve(navItem.path)}>{navItem.label}</a>
            </li>
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
            {@render navItemsSnippet(activeNavGroup.items)}
          </ul>
        </nav>
      {/if}
    </aside>
    <main>
      {@render children?.()}
    </main>
  </div>
</div>
{#snippet navItemsSnippet(items: readonly NavItem[])}
  {#each items as item (item.label)}
    {@render navItemSnippet(item)}
  {/each}
{/snippet}

{#snippet navItemSnippet(item: NavItem)}
  {#if "items" in item}
    <li>
      <details open={!item.collapsed}>
        <summary><span>{item.label}</span></summary>
        <ul>
          {@render navItemsSnippet(item.items)}
        </ul>
      </details>
    </li>
  {:else if "path" in item}
    {@const pagePath = resolve(item.path)}
    <li class:active={page.url.pathname === pagePath}>
      <a href={pagePath}>{item.label}</a>
    </li>
  {:else}
    <li>
      <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
      <a href={item.url}>{item.label}</a>
    </li>
  {/if}
{/snippet}

<style>
  .container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
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
      display: flex;
      margin: 0;
      margin-right: -8px;
      padding: 0;
      list-style: none;

      a {
        display: block;
        padding: 24px 16px;
        color: inherit;
        font-size: 14px;
      }
    }
  }

  .logo {
    display: flex;
    gap: 10px;
    align-items: center;
    font-weight: 700;
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
    flex: none;
    width: 260px;
    padding: 0 24px;
  }

  .search {
    & > ul {
      position: fixed;
      top: 0;
      left: 0;
      z-index: 10;
      width: 100vw;
      height: 100vh;
      background: #fff;
    }
  }

  .search-bar {
    display: flex;
    gap: 7px;
    align-items: center;
    margin: 24px 0;
    padding: 6px 8px;
    border: #7b9b9f;
    border-radius: 2px;
    background: #fff;
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
    border-bottom: 1px solid #a3a3a3;
  }

  .search-result-title {
    padding: 0 0 15px;
  }

  .search-result-excerpt {
    color: #666;
  }

  .nav-title {
    color: #415e63;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
  }

  .toc ul {
    margin: 0;
    margin-top: 12px;
    padding: 0;
    list-style: none;

    > li {
      border-radius: 6px;

      &.active {
        background-color: #fff;
      }

      a {
        display: block;
        padding: 8px 12px;
        color: inherit;
        font-size: 14px;
        line-height: 1.25;
      }
    }
  }

  main {
    flex: 1;
    margin-right: 24px;
    margin-bottom: 24px;
    border-radius: 12px;
    background: #fff;
  }
</style>
