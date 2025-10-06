<script lang="ts">
  let { data } = $props();
</script>

<div class="toc">
{@html data.toc}
</div>
{@html data.content}
{JSON.stringify(data.frontmatter)}

<style>
:global {
.shiki code {
  counter-reset: step;
  counter-increment: step 0;
}
.line::before {
  content: counter(step);
  counter-increment: step;
  width: 1rem;
  margin-right: 1.5rem;
  display: inline-block;
  text-align: right;
  color: rgba(115,138,148,.4);
}
}
</style>
