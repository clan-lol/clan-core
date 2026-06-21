<script lang="ts">
  import ClanLogo from "$lib/assets/icons/clan-logo.svg?component";
  import { Docs } from "$lib/models/docs.ts";
  import { resolve } from "$app/paths";
  import VersionSwitcher from "./VersionSwitcher.svelte";
  import WideSearchBar from "./WideSearchBar.svelte";
</script>

<header>
  <a class="logo" href={resolve(Docs.versionedBase)}
    ><ClanLogo height="22" /> Docs</a
  >
  <VersionSwitcher />
  <div class="search">
    <WideSearchBar />
  </div>
</header>

<style>
  header {
    position: relative;
    z-index: 1001;
    display: flex;
    grid-row: 1;
    grid-column: 1 / -1;
    gap: 14px;
    align-items: center;
    block-size: 60px;
    padding-inline: var(--docs-gutter-inline-start)
      var(--docs-gutter-inline-end);
    background: var(--bg-color);
  }

  .logo {
    display: flex;
    gap: 10px;
    align-items: center;
    color: inherit;
    font-weight: 700;
    font-size: 20px;
    text-decoration: none;
    font-variation-settings: "wdth" 112.5;
  }

  .search {
    position: absolute;
    inset: 0;
    z-index: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    pointer-events: none;
  }

  @media (--docs-top-bar-fixed) {
    header {
      position: sticky;
      inset-block-start: 0;
    }
  }
</style>
