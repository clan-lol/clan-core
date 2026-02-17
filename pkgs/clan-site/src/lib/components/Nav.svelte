<script lang="ts">
  import type { NavItem } from "~/lib/models/docs.ts";
  import ChevronRightIcon from "$lib/assets/icons/chevron-right.svg?component";
  import { page } from "$app/state";
  import { resolve } from "$app/paths";

  const {
    navItems,
    isVisible,
  }: {
    navItems: readonly NavItem[];
    isVisible: boolean;
  } = $props();
</script>

<nav class:is-visible={isVisible}>
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
        <summary><ChevronRightIcon height="17" />{item.label}</summary>
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
    padding: 0 14px;
    color: var(--secondary-fg-color);

    &.is-visible {
      display: block;
    }
  }

  summary {
    display: flex;
    gap: 3px;
    align-items: center;
    padding: 7px 0;
    list-style: none;
    font-size: 16px;

    :global(svg) {
      transition: 200ms;
    }

    details[open] > & {
      :global(svg) {
        transform: rotate(90deg);
      }
    }
  }

  ol {
    padding: 0;
    margin: 0;
    list-style: none;
  }

  li {
    position: relative;
    margin-inline-start: 20px;
    border-radius: 6px;

    &::before {
      content: "";
      position: absolute;
      inset-inline-start: -12px;
      inset-block: 0;
      z-index: 0;
      inline-size: 1px;
      background: var(--nav-indent-guide-color);
    }

    &.active {
      background-color: #fff;
    }

    a {
      display: block;
      padding: 9px 20px;
      color: inherit;
      font-size: 16px;
      line-height: 1.25;
    }

    nav > ol > & {
      margin-inline-start: 0;

      &::before {
        content: none;
      }
    }
  }
</style>
