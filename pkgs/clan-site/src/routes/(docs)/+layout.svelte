<script lang="ts">
  import ClanLogo from "$lib/assets/icons/clan-logo.svg?component";
  import MenuIcon from "$lib/assets/icons/menu.svg?component";
  import Nav from "~/lib/components/Nav.svelte";
  import { onNavigate } from "$app/navigation";
  import { page } from "$app/state";
  import Search from "~/lib/components/Search.svelte";
  import SearchIcon from "$lib/assets/icons/search.svg?component";

  const { data, children } = $props();
  const navItems = $derived(data.docsNavItems);
  const article = $derived(page.data.docsArticle);

  let headerMode: "search" | "nav" | undefined = $state();
  onNavigate(() => {
    headerMode = undefined;
    window.scrollTo(0, 0);
  });
</script>

<svelte:head>
  <title>{article?.title || "Clan Docs"}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    rel="preconnect"
    href="https://fonts.gstatic.com"
    crossorigin="anonymous"
  />
  <link
    href="https://fonts.googleapis.com/css2?family=Mona+Sans:ital,wdth,wght@0,100..112.5,200..900;1,100..112.5,200..900&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div data-page-id="docs">
  <header>
    <div class="logo"><ClanLogo height="22" /> Docs</div>
    <ol>
      <li class="search">
        <button title="Search"><SearchIcon height="18" /></button>
        <div class="input">
          <SearchIcon height="16" /> Search
        </div>
      </li>
      <li class="nav">
        <button
          title="Navigation"
          onclick={() => {
            headerMode = headerMode === "nav" ? undefined : "nav";
          }}><MenuIcon height="18" /></button
        >
      </li>
    </ol>
  </header>
  <main>
    <aside>
      <Search />
      <Nav
        {navItems}
        isVisible={headerMode === "nav"}
        navPath={article?.navPath ?? []}
      />
    </aside>
    {@render children?.()}
  </main>
</div>

<style>
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    /* safearea is always absolute */
    /* stylelint-disable-next-line csstools/use-logical */
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);

    > ol {
      display: flex;
      align-items: center;
      padding: 8px 0;
      margin: 0;
      list-style: none;

      button {
        display: flex;
        align-items: center;
        padding: 14px;
        color: inherit;
        background: none;
        border: 0;
        cursor: pointer;
      }

      .search .input {
        display: none;
      }
    }
  }

  .logo {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-inline-start: 14px;
    font-weight: 700;
    font-size: 20px;
    font-variation-settings: "wdth" 112.5;
  }

  @media (--wide) {
    header ol {
      padding-block: 16px;

      .search {
        margin-inline-end: 24px;

        button {
          display: none;
        }

        .input {
          display: flex;
          gap: 5px;
          align-items: center;
          inline-size: 200px;
          block-size: 35px;
          padding-inline-start: 8px;
          color: var(--input-fg-color);
          border: 1px solid var(--input-border-color);
          border-radius: 4px;
          font-size: 14px;
          cursor: text;
        }
      }

      .nav {
        display: none;
      }
    }

    .logo {
      margin-inline-start: 24px;
    }

    main {
      display: flex;
    }
  }
</style>
