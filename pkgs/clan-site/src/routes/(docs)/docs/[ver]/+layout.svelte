<script lang="ts">
  import ArrowLeftIcon from "$lib/assets/icons/arrow-left.svg?component";
  import ArrowRightIcon from "$lib/assets/icons/arrow-right.svg?component";
  import { page } from "$app/state";
  import { resolve } from "$app/paths";

  const { children } = $props();
  const article = $derived(page.data.docsArticle);
</script>

<div class="container">
  <article>
    <div class="inner">
      {@render children()}
    </div>
  </article>
  <footer>
    {#if article?.previous}
      <a class="pointer" href={resolve(article.previous.path)}>
        <dl>
          <dt><ArrowLeftIcon height="12" /> Previous</dt>
          <dd>{article.previous.label}</dd>
        </dl>
      </a>
    {:else}
      <div class="pointer empty"></div>
    {/if}
    {#if article?.next}
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

  @media (--wide) {
    .container {
      flex: 1;
      min-inline-size: 0;
      margin-inline-end: 24px;
    }

    article {
      padding-inline: 24px;
      border-end-start-radius: 14px;
      border-end-end-radius: 14px;
    }

    .inner {
      max-inline-size: 600px;
      margin: 0 auto;
    }

    footer {
      gap: 24px;
      margin: 24px 0;
    }

    .pointer {
      padding: 20px;
    }
  }
</style>
