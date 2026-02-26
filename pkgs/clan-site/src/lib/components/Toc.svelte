<script lang="ts">
  import type { Toc, TocItem, TocItems } from "../models/toc.svelte.ts";
  import ChevronRightIcon from "$lib/assets/icons/chevron-right.svg?component";

  let { toc }: { toc: Toc } = $props();
</script>

<header class:is-expended={toc.isExpanded}>
  <nav>
    <button use:toc.setHeight onclick={toc.onClickTitle}>
      {#if toc.isExpanded || !toc.activeTocItem}
        Table of contents
      {:else}
        {toc.activeTocItem.label}
      {/if}
      <ChevronRightIcon height="16" />
    </button>
    <div class="menu">
      {@render tocTree(toc.tocItems)}
    </div>
  </nav>
</header>

{#snippet tocTree(items: TocItems)}
  <ol>
    {#each items as item (item.id)}
      {@render tocBranch(item)}
    {/each}
  </ol>
{/snippet}

{#snippet tocBranch(item: TocItem)}
  <li>
    <a href={`#${item.id}`} onclick={item.onClick}>{item.label}</a>
    {#if "children" in item}
      {@render tocTree(item.children)}
    {/if}
  </li>
{/snippet}

<style>
  header {
    position: sticky;
    inset-block-start: 0;
    z-index: 100;
    margin-inline: -14px;
    color: var(--toc-fg-color);
    background: var(--toc-bg-color);
    border-block-end: 1px solid var(--toc-border-color);
    border-start-start-radius: 14px;
    border-start-end-radius: 14px;
    font-weight: 500;
    font-size: 16px;
  }

  nav {
    > button {
      display: flex;
      gap: 5px;
      align-items: center;
      inline-size: 100%;
      padding: 14px;
      color: var(--toc-title-fg-color);
      background: transparent;
      border: 0;
      font: inherit;
      cursor: pointer;
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
      inset-inline-start: 0;
      inset-block: 0;
      z-index: 0;
      inline-size: 1px;
      background: var(--toc-indent-guide-color);
    }

    a {
      position: relative;
      display: block;
      padding: 5px 20px;
      color: inherit;
      text-decoration: none;

      &::before {
        content: "";
        position: absolute;
        inset-inline-start: 0;
        inset-block: 0;
        z-index: 0;
        inline-size: 1px;
        background: var(--toc-indent-guide-color);
      }

      &:hover::before {
        background: var(--toc-highlighted-indent-guide-color);
      }

      &:hover {
        color: var(--toc-highlighted-fg-color);
        background: var(--toc-highlighted-bg-color);
      }
    }
  }

  .menu {
    position: absolute;
    inset-inline: 0;
    display: none;
    padding-block: 9px;
    margin-block-start: 1px;
    background: var(--toc-bg-color);
    border-end-start-radius: 14px;
    border-end-end-radius: 14px;
    box-shadow: 0 3px 5px #00000020;

    > ol {
      > li {
        margin-inline-start: 0;

        &::before {
          content: none;
        }

        > a {
          padding-inline: 14px;

          &::before {
            content: none;
          }
        }

        > ol > li {
          margin-inline-start: 14px;
        }
      }
    }
  }

  .is-expended .menu {
    display: block;
  }

  @media (--medium) {
    header {
      margin-inline: -28px;
    }

    nav {
      > button {
        padding-inline: 28px;
      }
    }

    .menu > ol {
      position: static;
      margin-inline: 28px;

      > li {
        margin-inline: -14px;
      }
    }
  }

  @media (--wide) {
    header {
      flex: none;
      align-self: start;
      order: 2;
      inline-size: 260px;
      margin-inline: 0;
      border-block-end: 0;
    }

    nav {
      > button {
        padding: 18px 24px;
        font-weight: 600;

        :global(svg) {
          display: none;
        }
      }
    }

    li {
      margin-inline-start: 24px;

      a {
        padding: 8px 24px;
      }
    }

    .menu {
      display: block;
      padding-block: 0;
      box-shadow: none;

      > ol {
        margin-inline: 0;

        > li {
          margin-inline: 0;

          > a {
            padding-inline: 24px;
          }

          > ol > li {
            margin-inline-start: 24px;
          }
        }
      }
    }
  }
</style>
