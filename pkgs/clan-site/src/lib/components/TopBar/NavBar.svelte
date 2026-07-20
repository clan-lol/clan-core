<script lang="ts">
  import ClanLogo from "$lib/assets/icons/clan-logo.svg?component";
  import { Docs, getDocsContext } from "$lib/models/docs.ts";
  import NavToggler from "./NavToggler.svelte";
  import { resolve } from "$app/paths";
  import SearchIcon from "$lib/assets/icons/search.svg?component";
  import VersionSwitcher from "./VersionSwitcher.svelte";

  const docs = getDocsContext();
</script>

<div class="container" class:rotated={docs.topbarMode === "search"}>
  <div class="inner">
    <div class="main">
      <a class="logo" href={resolve(Docs.versionedBase)}
        ><ClanLogo height="22" /> Docs</a
      >
      <VersionSwitcher />
    </div>
    <ol>
      <li>
        <button
          class="search-button"
          title="Search"
          onclick={(): void => {
            docs.topbarMode = "search";
          }}><SearchIcon height="18" /></button
        >
      </li>
      <li>
        <NavToggler />
      </li>
    </ol>
  </div>
</div>

<style>
  .container {
    padding-inline: var(--docs-gutter-inline-start)
      var(--docs-gutter-inline-end);
    background: var(--bg-color);
    transition: var(--top-bar-toggle-duration);

    &.rotated {
      background-color: color-mix(in srgb, var(--bg-color), #000 15%);
    }
  }

  .inner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    block-size: 60px;
  }

  .main {
    display: flex;
    gap: 14px;
    align-items: center;
    margin: 0;
  }

  ol {
    display: flex;
    align-self: stretch;
    padding: 0;
    margin: 0;
    list-style: none;
  }

  li {
    display: flex;
  }

  .search-button {
    padding: 0 14px;
    color: inherit;
    background: none;
    border: 0;
    cursor: pointer;
  }

  .logo {
    display: flex;
    gap: 10px;
    align-items: center;
    color: inherit;
    font-weight: 700;
    font-size: 20px;
    text-decoration: none;
    font-variation-settings: "width" 112.5;
  }

  @media (--docs-tablet) {
    .container {
      transition: none;
    }
  }
</style>
