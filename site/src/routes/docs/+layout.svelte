<script lang="ts">
  import type { NormalizedNavLink } from "./utils";
  let { children, data } = $props();
</script>

{#snippet navLinkSnippet(navLink: NormalizedNavLink)}
  {#if "items" in navLink}
    <li>
      <span class="label group">{navLink.label}</span>
      <ul>
        {#each navLink.items as item}
          {@render navLinkSnippet(item)}
        {/each}
      </ul>
    </li>
  {:else}
    <li>
      <a href={navLink.slug}>{navLink.label}</a>
    </li>
  {/if}
{/snippet}

<div class="container">
  <nav>
    <ul>
      {#each data.navLinks as navLink}
        {@render navLinkSnippet(navLink)}
      {/each}
    </ul>
  </nav>
  <div class="content">
    {@render children()}
  </div>
</div>

<style>
  .container {
    display: flex;
  }
  nav {
    width: 300px;
    flex: none;
  }
</style>
