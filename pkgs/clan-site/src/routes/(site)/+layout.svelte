<script lang="ts">
  import config from "$config";
  import { resolve } from "$app/paths";
  import "~/base.css";

  const { children } = $props();
</script>

<header>
  <nav>
    <ol>
      <li><a href={resolve("/")}>Home</a></li>
      <li><a href={resolve(`/docs/${config.ver}`)}>Documentation</a></li>
    </ol>
  </nav>
</header>
<main>
  {@render children()}
</main>
