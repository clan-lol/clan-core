<script lang="ts">
  import "./markdown.css";
  import "./shiki.css";
  import "./admonition.css";
  let { data } = $props();
</script>

<div class="container">
  <div class="content">
    <h1>{data.frontmatter.title}</h1>
    {@html data.content}
  </div>
  <div class="toc">
    <h2>On this page</h2>
    {@html data.toc}
  </div>
</div>

<!-- {JSON.stringify(data.frontmatter)} -->
<style>
  .container {
    display: flex;
    padding-left: 30px;
  }
  .content {
    flex: 1;
    max-width: 800px;
    margin-left: calc(50vw - 400px - 300px);
  }
  .toc {
    flex: none;
  }
</style>
