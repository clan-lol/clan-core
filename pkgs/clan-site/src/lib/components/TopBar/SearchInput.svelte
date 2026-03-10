<script lang="ts">
  import { getDocsContext } from "#lib/models/docs.ts";

  const docs = getDocsContext();

  const { fake = false }: { fake?: boolean } = $props();
</script>

{#if fake}
  <input
    class="fake"
    bind:this={docs.search.fakeInputElement}
    type="text"
    placeholder="Search"
    bind:value={docs.search.query}
  />
{:else}
  <input
    class="real"
    class:visible={docs.topbarMode === "search"}
    bind:this={docs.search.inputElement}
    type="search"
    bind:value={docs.search.query}
  />
{/if}

<style>
  input {
    background: transparent;
    border: none;
    outline: none;
    font: inherit;
    font-size: inherit;
  }

  .fake {
    flex: 1;
    block-size: 35px;
    margin-inline: 7px 12px;
    color: transparent;

    &::placeholder {
      color: var(--search-input-placeholder-color);
    }
  }

  .real {
    position: absolute;
    color: var(--fg-color);
    opacity: 0;
    transition: 0ms 400ms;

    &.visible {
      opacity: 1;
    }
  }
</style>
