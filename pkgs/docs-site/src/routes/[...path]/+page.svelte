<script lang="ts">
  import "$lib/markdown/main.css";
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

<style>
  .container {
    display: flex;
  }
  .content {
    padding: 0 15px;
    width: 100vw;
    word-break: break-word;
  }
  .toc {
    display: none;
    flex: none;
  }
</style>
