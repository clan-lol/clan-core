<script lang="ts">
  import config from "$config";
  import { resolve } from "$app/paths";

  const { children } = $props();
</script>

<header>
  <nav>
    <ol>
      <li><a href={resolve("/")}>Home</a></li>
      <li><a href={resolve(config.docsBase)}>Documentation</a></li>
    </ol>
  </nav>
</header>
<main>
  {@render children()}
</main>
