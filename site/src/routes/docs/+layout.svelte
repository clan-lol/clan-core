<script lang="ts">
  import type { NavLink } from ".";
  let { children, data } = $props();
  let docs = $derived(data.docs!);
</script>

{#snippet navLinks(nLinks: NavLink[])}
  <ul>
    {#each nLinks as nLink}
      {@render navLink(nLink)}
    {/each}
  </ul>
{/snippet}

{#snippet navLink(nLink: NavLink)}
  {#if "items" in nLink}
    <li>
      <details open={!nLink.collapsed}>
        <summary><span class="label group">{nLink.label}</span></summary>
        {@render navLinks(nLink.items)}
      </details>
    </li>
  {:else}
    <li>
      <a href={nLink.link}>{nLink.label}</a>
    </li>
  {/if}
{/snippet}

<div class="container">
  <nav>
    {@render navLinks(docs.navLinks)}
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
  }

  summary {
    list-style: none;
    cursor: pointer;
  }
</style>
