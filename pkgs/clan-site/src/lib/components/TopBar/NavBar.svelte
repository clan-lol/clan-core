<script lang="ts">
  import ClanLogo from "$lib/assets/icons/clan-logo.svg?component";
  import { docsBase } from "$config";
  import { getDocsContext } from "~/lib/models/docs.ts";
  import NavToggler from "./NavToggler.svelte";
  import { resolve } from "$app/paths";
  import SearchToggler from "./SearchToggler.svelte";

  const docs = getDocsContext();
</script>

<div class="container" class:rotated={docs.topbarMode === "search"}>
  <a class="logo" href={resolve(docsBase)}><ClanLogo height="22" /> Docs</a>
  <ol>
    <li>
      <SearchToggler />
    </li>
    <li>
      <NavToggler />
    </li>
  </ol>
</div>

<style>
  .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    block-size: 60px;
    /* safearea is always absolute */
    /* stylelint-disable-next-line csstools/use-logical */
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
    background: var(--bg-color);
    transition: 400ms;

    &.rotated {
      background-color: color-mix(in srgb, var(--bg-color), #000 15%);
    }
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
    margin-inline-start: 14px;
    color: inherit;
    font-weight: 700;
    font-size: 20px;
    text-decoration: none;
    font-variation-settings: "wdth" 112.5;
  }

  @media (--medium) {
    .container {
      transition: none;

      &.rotated {
        display: none;
      }
    }
  }

  @media (--wide) {
    .logo {
      margin-inline-start: 24px;
    }

    .inner {
      block-size: 90px;
    }
  }
</style>
