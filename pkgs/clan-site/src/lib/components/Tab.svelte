<script lang="ts">
  import type { Snippet } from "svelte";
  import { getTabsContext } from "$lib/models/tabs.ts";

  const { title, children }: { title: string; children?: Snippet } = $props();
  const tabs = getTabsContext();
  const tab = tabs.addTab(() => title);
</script>

<section class:open={tab.isActive}>
  <div class="title">{title}</div>
  <div class="content">
    {@render children?.()}
  </div>
</section>

<style>
  .title {
    display: block;
    inline-size: 100%;
    padding: 8px 14px;
    border-block-start: 1px solid var(--tabs-border-color);
    border-block-end: 1px solid var(--tabs-border-color);
    font-weight: 500;
    font-size: 16px;
    text-align: start;
    cursor: pointer;

    section:first-of-type > & {
      border-block-start: 0;
    }
  }

  .content {
    margin: 14px;
  }

  :global(.js) {
    .title {
      display: none;
    }

    .content {
      display: none;
    }

    .open .content {
      display: block;
    }
  }
</style>
