<script lang="ts">
  import type { NavItem } from "~/lib/models/docs.ts";
  import ChevronRightIcon from "$lib/assets/icons/chevron-right.svg?component";
  import { resolve } from "$app/paths";

  const {
    navItems,
    isVisible,
    navPath,
  }: {
    navItems: readonly NavItem[];
    isVisible: boolean;
    navPath: readonly number[];
  } = $props();
</script>

<nav class:is-visible={isVisible}>
  {@render navTree(navItems, navPath)}
</nav>

{#snippet navTree(items: readonly NavItem[], navPath: readonly number[])}
  <ol>
    {#each items as item, i (item.label)}
      {@render navBranch(item, i, navPath)}
    {/each}
  </ol>
{/snippet}

{#snippet navBranch(item: NavItem, i: number, navPath: readonly number[])}
  {#if "children" in item}
    <li>
      <details open={i === navPath[0]}>
        <summary><ChevronRightIcon height="17" />{item.label}</summary>
        {@render navTree(
          item.children,
          i === navPath[0] ? navPath.slice(1) : [],
        )}
      </details>
    </li>
  {:else if "path" in item}
    <li class:active={i === navPath[0]}>
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
    cursor: pointer;

    &:hover {
      color: var(--fg-color);
    }

    :global(svg) {
      transition: 200ms;
    }

    details[open] > & :global(svg) {
      transform: rotate(90deg);
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

    &::before {
      content: "";
      position: absolute;
      inset-inline-start: -12px;
      inset-block: 0;
      z-index: 0;
      inline-size: 1px;
      background: var(--nav-indent-guide-color);
    }

    a {
      display: block;
      padding: 9px 20px;
      color: inherit;
      border-radius: 6px;
      font-size: 16px;
      line-height: 1.25;

      &:hover {
        color: var(--fg-color);
        background-color: var(--secondary-bg-color);
      }
    }

    &.active a {
      color: var(--fg-color);
      background-color: var(--content-bg-color);
    }

    nav > ol > & {
      margin-inline-start: 0;

      &::before {
        content: none;
      }
    }
  }
</style>
