<script>
  let { data, children } = $props();
  let { paths } = data;
</script>

<nav>
  {#each paths as path}
    <li><a href={`/docs/${path}`}>{path}</a></li>
  {/each}
  <li><a href="/">Home</a></li>
</nav>
{@render children()}
