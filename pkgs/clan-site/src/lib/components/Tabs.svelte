<script lang="ts">
  import type { Snippet } from "svelte";
  import { setTabsContext, Tabs } from "$lib/models/tabs.ts";

  const { children }: { children?: Snippet } = $props();
  const tabs = new Tabs();
  setTabsContext(tabs);
</script>

<!-- We table code blocks specially inside .tabs -->
<!-- eslint-disable-next-line svelte/no-unused-class-name -->
<article class="tabs">
  {#if tabs.all.length !== 0}
    <ol>
      {#each tabs.all as tab, i (i)}
        <li class:open={tab.isActive}>
          <button onclick={(): void => tab.activate()}>{tab.title}</button>
        </li>
      {/each}
    </ol>
  {/if}
  <div class="inner">
    {@render children?.()}
  </div>
</article>

<style>
  article {
    overflow: hidden;
    border: 1px solid var(--tabs-border-color);
    border-radius: 8px;
  }

  ol {
    display: none;
  }

  :global(.js) {
    article {
      border: 0;
      border-radius: 0;
    }

    .inner {
      border: 1px solid var(--tabs-border-color);
      border-radius: 8px;
      border-start-start-radius: 0;
      border-start-end-radius: 0;
    }

    ol {
      display: flex;
      padding: 0;
      margin: 0;
      list-style: none;
    }

    li {
      display: flex;
      align-items: center;
    }

    button {
      padding: 12px 14px;
      margin-block-end: -1px;
      background: transparent;
      border: 1px solid transparent;
      border-block-end: 0;
      font-weight: 500;
    }

    .open button {
      background: var(--content-bg-color);
      border-color: var(--tabs-border-color);
      border-start-start-radius: 8px;
      border-start-end-radius: 8px;
    }
  }
</style>
