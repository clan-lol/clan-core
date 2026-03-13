<script lang="ts">
  import ClanLogo from "$lib/assets/icons/clan-logo.svg?component";
  import { Docs, getDocsContext } from "$lib/models/docs.ts";
  import NavToggler from "./NavToggler.svelte";
  import { resolve } from "$app/paths";
  import SearchToggler from "./SearchToggler.svelte";
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
        <SearchToggler />
      </li>
      <li>
        <NavToggler />
      </li>
    </ol>
  </div>
</div>

<style>
  .container {
    /* safearea is always absolute */
    /* stylelint-disable-next-line csstools/use-logical */
    padding-left: max(14px, env(safe-area-inset-left));
    padding-right: max(14px, env(safe-area-inset-right));
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

  @media (--docs-tablet) {
    .container {
      transition: none;
    }
  }

  @media (--docs-desktop) {
    .container {
      padding: 0 24px;
    }
  }
</style>
