<script lang="ts">
  import type { NavLink } from "./utils";
  let { children, data } = $props();
</script>

{#snippet navLinkSnippet(navLink: NavLink)}
  {#if "items" in navLink}
    <li>
      <details open={!navLink.collapsed}>
        <summary><span class="label group">{navLink.label}</span></summary>
        <ul>
          {#each navLink.items as item}
            {@render navLinkSnippet(item)}
          {/each}
        </ul>
      </details>
    </li>
  {:else}
    <li>
      <a href={navLink.link}>{navLink.label}</a>
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
    display: none;
    width: 300px;
    flex: none;
  }

  summary {
    list-style: none;
    cursor: pointer;
  }
</style>
