<script lang="ts">
  import "./shiki.css";
  import "./admonition.css";
  let { data } = $props();
</script>

<div class="toc">
{@html data.toc}
</div>
{@html data.content}
{JSON.stringify(data.frontmatter)}
