<script lang="ts">
  import type { NavItem } from "~/lib/models/docs.ts";
  import { page } from "$app/state";
  import { resolve } from "$app/paths";

  interface Props {
    navItems: readonly NavItem[];
  }

  const { navItems }: Props = $props();
</script>

<nav>
  {@render navTree(navItems)}
</nav>
{#snippet navTree(items: readonly NavItem[])}
  <ol>
    {#each items as item (item.label)}
      {@render navBranch(item)}
    {/each}
  </ol>
{/snippet}

{#snippet navBranch(item: NavItem)}
  {#if "children" in item}
    <li>
      <details open={!item.collapsed}>
        <summary><span>{item.label}</span></summary>
        {@render navTree(item.children)}
      </details>
    </li>
  {:else if "path" in item}
    <li class:active={page.url.pathname === resolve(item.path)}>
      <a href={resolve(item.path)}>{item.label}</a>
    </li>
  {:else}
    <li>
      <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
      <a href={item.url}>{item.label}</a>
    </li>
  {/if}
{/snippet}

<style>
  nav {
    display: none;
  }

  ol {
    padding: 0;
    margin: 0;
    margin-block-start: 12px;
    list-style: none;
  }

  li {
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
</style>
