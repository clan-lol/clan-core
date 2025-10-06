<script lang="ts">
  let { data } = $props();
  let { content, toc, frontmatter } = data;
</script>

<div class="toc">
{@html toc}
</div>
{@html content}
{JSON.stringify(frontmatter)}

<style>
  .toc :global(p) {
    margin: 0;
  }
</style>
