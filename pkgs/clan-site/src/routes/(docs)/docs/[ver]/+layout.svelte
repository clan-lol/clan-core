<script lang="ts">
  import ArrowLeftIcon from "$lib/assets/icons/arrow-left.svg?component";
  import ArrowRightIcon from "$lib/assets/icons/arrow-right.svg?component";
  import { getDocsContext } from "~/lib/models/docs.ts";
  import { resolve } from "$app/paths";
  import Toc from "$lib/components/Toc.svelte";

  const { children } = $props();
  const docs = getDocsContext();
  const article = $derived(docs.article);
  const toc = $derived(article.toc);
</script>

<div class="container" class:no-toc={toc.items.length === 0}>
  <article>
    <div class="article-inner">
      {#if toc.items.length !== 0}
        <Toc />
      {/if}
      <div class="content" use:toc.setContent>
        {@render children()}
      </div>
    </div>
  </article>
  <footer>
    {#if article.prev}
      <a class="pointer" href={resolve(article.prev.path)}>
        <dl>
          <dt><ArrowLeftIcon height="12" /> Previous</dt>
          <dd>{article.prev.label}</dd>
        </dl>
      </a>
    {:else}
      <div class="pointer empty"></div>
    {/if}
    {#if article.next}
      <a class="pointer next" href={resolve(article.next.path)}>
        <dl>
          <dt>Next <ArrowRightIcon height="12" /></dt>
          <dd>{article.next.label}</dd>
        </dl>
      </a>
    {:else}
      <div class="pointer next empty"></div>
    {/if}
  </footer>
</div>

<style>
  article {
    /* safearea is always absolute */
    /* stylelint-disable-next-line csstools/use-logical */
    padding-left: max(14px, env(safe-area-inset-left));
    padding-right: max(14px, env(safe-area-inset-right));
    color: var(--content-fg-color);
    background: var(--content-bg-color);
    border: 1px solid var(--content-border-color);
    border-radius: 14px;
    border-end-start-radius: 0;
    border-end-end-radius: 0;
  }

  footer {
    display: flex;
    gap: 14px;
    justify-content: space-between;
    margin: 14px;
  }

  .pointer {
    flex: 1;
    gap: 10px;
    align-items: center;
    padding: 14px;
    color: inherit;
    background: var(--content-bg-color);
    border: 1px solid var(--content-border-color);
    border-radius: 14px;
    text-decoration: none;

    &.next {
      text-align: end;
    }

    &.empty {
      background-color: transparent;
      border: 0;
    }
  }

  dl {
    margin: 0;
  }

  dt {
    display: flex;
    gap: 5px;
    align-items: center;
    font-size: 14px;

    .pointer.next & {
      justify-content: end;
    }
  }

  dd {
    margin: 0;
  }

  @media (--medium) {
    .container {
      flex: 1;
      min-inline-size: 0;
      margin-inline-end: 14px;
    }

    article {
      padding-inline: 28px;
      border-end-start-radius: 14px;
      border-end-end-radius: 14px;

      .no-toc & {
        padding-inline: 0;
      }
    }

    .no-toc .article-inner {
      inline-size: 90%;
      margin-inline: auto;
    }

    footer {
      gap: 14px;
      margin: 14px 0;
    }

    .pointer {
      padding: 20px;
    }
  }

  @media (--wide) {
    .container {
      margin-inline-end: 24px;
    }

    article {
      padding-inline: 0;
    }

    .article-inner {
      display: flex;
      max-inline-size: calc(800px + 290px);
      margin-inline: auto;

      .no-toc & {
        display: block;
        inline-size: 80%;
        max-inline-size: 800px;
      }
    }

    .content {
      flex: 1;
      min-inline-size: 0;
      padding-inline: 28px;

      .no-toc & {
        padding-inline: 0;
      }
    }

    footer {
      gap: 24px;
      margin: 24px 0;
    }
  }
</style>
