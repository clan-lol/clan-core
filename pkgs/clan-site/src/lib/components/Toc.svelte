<script lang="ts">
  import type { TocItem, TocItems } from "../models/docs/toc.svelte.ts";
  import ArrowTopIcon from "$lib/assets/icons/arrow-top.svg?component";
  import ChevronRightIcon from "$lib/assets/icons/chevron-right.svg?component";
  import { getDocsContext } from "#lib/models/docs.ts";

  const docs = getDocsContext();
  const toc = $derived(docs.article.toc);

  const topBarHeight = 60;
  let scrollY = $state(0);
  function scrollToTop(): void {
    toc.open = false;
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }
</script>

<svelte:window bind:scrollY />

<header class:open={toc.open}>
  <nav>
    <button class="toc-title" use:toc.setHeight onclick={toc.onClickTitle}>
      <span>
        {#if toc.open || !toc.activeTocItem}
          On This Page
        {:else}
          {toc.activeTocItem.label}
        {/if}
      </span>
      <ChevronRightIcon height="16" />
    </button>
    <button
      class="scroll-to-top"
      class:hidden={scrollY < topBarHeight}
      onclick={scrollToTop}><ArrowTopIcon height="14" /></button
    >
    <div class="menu">
      {@render tocTree(toc.items)}
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
    <a href={`#${item.id}`} onclick={item.onClick}><span>{item.label}</span></a>
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
    /* safearea is always absolute */
    /* stylelint-disable-next-line csstools/use-logical */
    padding-left: max(14px, env(safe-area-inset-left));
    padding-right: max(14px, env(safe-area-inset-right));
    color: var(--toc-fg-color);
    background: var(--toc-bg-color);
    border-block-end: 1px solid var(--toc-border-color);
    border-start-start-radius: 14px;
    border-start-end-radius: 14px;
    font-weight: 500;
    font-size: 16px;
  }

  nav {
    display: flex;
  }

  .toc-title {
    display: flex;
    flex: 1;
    gap: 5px;
    align-items: center;
    min-inline-size: 0;
    padding: 14px;
    margin-inline-start: -14px;
    color: var(--toc-title-fg-color);
    background: transparent;
    border: 0;
    font: inherit;
    cursor: pointer;

    > span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .scroll-to-top {
    position: relative;
    flex: none;
    padding: 8px 14px;
    margin-inline-end: -14px;
    color: inherit;
    background: transparent;
    border: 0;
    cursor: pointer;

    &::before {
      content: "";
      position: absolute;
      inset-inline-start: 0;
      inset-block: 12px;
      border-inline-start: 1px solid var(--toc-border-color);
    }

    &.hidden {
      display: none;
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

      > span {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }

  .menu {
    position: absolute;
    inset-inline: 0;
    inset-block-start: 100%;
    display: none;
    overflow: auto;
    max-block-size: 60vh;
    padding-block: 9px;
    margin-block-start: 1px;
    background: var(--toc-bg-color);
    border-end-start-radius: 14px;
    border-end-end-radius: 14px;
    box-shadow: 0 3px 5px var(--toc-shadow-color);

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

  .open .menu {
    display: block;
  }

  @media (--medium) {
    header {
      padding-inline: 0;
    }

    .toc-title,
    .scroll-to-top {
      padding-inline: 24px;
    }

    .toc-title {
      margin-inline-start: 0;
    }

    .scroll-to-top {
      margin-inline-end: 0;
    }

    .menu > ol {
      position: static;
      margin-inline: 24px;

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
      overflow: auto;
      inline-size: 260px;
      max-block-size: 100vh;
      padding-block: 12px 24px;
      margin-inline: 0;
      margin-block-start: 14px;
      border-block-end: 0;
    }

    nav {
      display: block;
    }

    .toc-title {
      padding: 18px 24px;
      font-weight: 600;

      :global(svg) {
        display: none;
      }
    }

    .scroll-to-top {
      display: none;
    }

    li {
      margin-inline-start: 24px;

      a {
        padding: 8px 24px;
      }
    }

    .menu {
      position: static;
      display: block;
      overflow: visible;
      max-block-size: none;
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
