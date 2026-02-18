<script lang="ts">
  const { children } = $props();
</script>

<article>
  <div class="inner">
    {@render children()}
  </div>
</article>

<style>
  article {
    /* safearea is always absolute */
    /* stylelint-disable-next-line csstools/use-logical */
    padding-left: max(14px, env(safe-area-inset-left));
    padding-right: max(14px, env(safe-area-inset-right));
    color: var(--content-fg-color);
    background: var(--content-bg-color);
    border: 1px solid var(--nav-border-color);
    border-radius: 14px;
  }

  @media (--wide) {
    article {
      flex: 1;
      min-inline-size: 0;
      padding-inline: 24px;
      margin-inline-end: 24px;
    }

    .inner {
      max-inline-size: 600px;
      margin: 0 auto;
    }
  }
</style>
