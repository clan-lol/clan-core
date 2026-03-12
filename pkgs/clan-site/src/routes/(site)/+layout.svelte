<script lang="ts">
  import { Docs } from "#lib/models/docs.ts";
  import { resolve } from "$app/paths";

  const { children } = $props();
</script>

<header>
  <nav>
    <ol>
      <li><a href={resolve("/")}>Home</a></li>
      <li><a href={resolve(Docs.versionedBase)}>Documentation</a></li>
    </ol>
  </nav>
</header>
<main>
  {@render children()}
</main>
