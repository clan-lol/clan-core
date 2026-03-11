<script lang="ts">
  import type { NavItem, NavItems } from "$lib/models/docs.ts";
  import ChevronRightIcon from "$lib/assets/icons/chevron-right.svg?component";
  import { getDocsContext, NavGroup, NavPathItem } from "$lib/models/docs.ts";
  import { resolve } from "$app/paths";

  const docs = getDocsContext();
  const nav = $derived(docs.nav);
</script>

<nav class:open={nav.open}>
  <div class="inner">
    {@render navTree(nav.items)}
  </div>
</nav>

{#snippet navTree(items: NavItems)}
  <ol>
    {#each items as item, i (i)}
      {@render navBranch(item)}
    {/each}
  </ol>
{/snippet}

{#snippet navBranch(item: NavItem)}
  {#if item instanceof NavGroup}
    <li>
      <details bind:open={item.open}>
        <summary><ChevronRightIcon height="17" />{item.label}</summary>
        {@render navTree(item.children)}
      </details>
    </li>
  {:else if item instanceof NavPathItem}
    <li class:active={item.isActive}>
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
    /* safearea is always absolute */
    /* stylelint-disable-next-line csstools/use-logical */
    padding-left: max(14px, env(safe-area-inset-left));
    padding-right: max(14px, env(safe-area-inset-right));
    color: var(--secondary-fg-color);
    font-weight: 500;
    font-size: 14px;

    &.open {
      display: block;
    }
  }

  summary {
    display: flex;
    gap: 3px;
    align-items: center;
    padding: 7px 0;
    list-style: none;
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
      padding-inline: 20px 14px;
      padding-block: 9px;
      color: inherit;
      border-radius: 6px;
      line-height: 1.25;
      text-decoration: none;

      &:hover {
        color: var(--fg-color);
        background-color: var(--secondary-bg-color);
      }
    }

    &.active a {
      color: var(--fg-color);
      background-color: var(--content-bg-color);
    }

    .inner > ol > & {
      margin-inline-start: 0;

      &::before {
        content: none;
      }
    }
  }

  @media (--medium) {
    nav {
      display: block;
      grid-row: 2;
      grid-column: 1;
      inline-size: 280px;
      padding-inline-end: 14px;
    }

    .inner {
      position: sticky;
      inset-block-start: 0;
      overflow: auto;
      max-block-size: 100vh;
      padding-block-end: 14px;
    }
  }

  @media (--wide) {
    nav {
      padding-inline: 24px 14px;
    }
  }
</style>
