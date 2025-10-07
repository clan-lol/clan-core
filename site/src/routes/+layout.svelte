<script lang="ts">
  import "./index.css";

  import favicon from "$lib/assets/favicon.svg";

  let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<nav>
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/docs/">Docs</a></li>
  </ul>
</nav>
<main>
  {@render children?.()}
</main>

<style>
  ul {
    display: flex;
    border-bottom: 1px solid;
    list-style: none;
  }
  li {
    padding-left: 2em;
  }
</style>
