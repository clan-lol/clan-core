<script lang="ts">
  import "./shiki.css";
  import "./admonition.css";
  let { data } = $props();
</script>

<div class="container">
  <div class="content">
    {@html data.content}
  </div>
  <div class="toc">
    {@html data.toc}
  </div>
</div>

<!-- {JSON.stringify(data.frontmatter)} -->
<style>
  .container {
    display: flex;
  }
</style>
