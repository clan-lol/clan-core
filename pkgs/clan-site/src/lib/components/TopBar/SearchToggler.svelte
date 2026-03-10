<script lang="ts">
  import { getDocsContext } from "#lib/models/docs.ts";
  import SearchIcon from "$lib/assets/icons/search.svg?component";

  const docs = getDocsContext();
</script>

<button
  class="button"
  title="Search"
  onclick={(): void => {
    docs.topbarMode = "search";
  }}><SearchIcon height="18" /></button
>
<button
  class="input"
  onclick={(): void => {
    docs.topbarMode = "search";
  }}
>
  <SearchIcon height="16" /> Search
</button>

<style>
  .button {
    padding: 0 14px;
    color: inherit;
    background: none;
    border: 0;
    cursor: pointer;
  }

  .input {
    display: none;
  }

  @media (--medium) {
    .button {
      display: none;
    }

    .input {
      display: flex;
      gap: 5px;
      align-items: center;
      align-self: center;
      inline-size: 220px;
      block-size: 35px;
      padding-inline-start: 11px;
      margin-inline-end: 14px;
      color: var(--search-fg-color);
      background: transparent;
      border: 1px solid var(--search-border-color);
      border-radius: 999em;
      font-size: 14px;
      cursor: text;
    }
  }

  @media (--wide) {
    .input {
      margin-inline-end: 24px;
    }
  }
</style>
