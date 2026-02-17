<script lang="ts">
  const { children } = $props();
</script>

<article>
  {@render children()}
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
</style>
