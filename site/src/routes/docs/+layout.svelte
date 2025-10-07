<script>
  let { data, children } = $props();
  let { paths } = data;
</script>

<div class="container">
  <nav>
    {#each paths as path}
      <li><a href={`/docs/${path}`}>{path}</a></li>
    {/each}
    <li><a href="/">Home</a></li>
  </nav>
  <div class="content">
    {@render children()}
  </div>
</div>

<style>
  .container {
    display: flex;
  }
</style>
