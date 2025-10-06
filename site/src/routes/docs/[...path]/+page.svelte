<script lang="ts">
  let { data } = $props();
</script>

<div class="toc">
{@html data.toc}
</div>
{@html data.content}
{JSON.stringify(data.frontmatter)}

<style>
  .toc :global(p) {
    margin: 0;
  }
</style>
