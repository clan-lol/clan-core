<script lang="ts">
  import favicon from "$lib/assets/favicon.svg";
  import type { NavLink } from "$lib";
  import { onNavigate } from "$app/navigation";
  import "./index.css";

  const { data, children } = $props();
  const docs = $derived(data.docs);
  let menuOpen = $state(false);
  onNavigate(() => {
    menuOpen = false;
  });
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<div class="global-bar">
  <span class="logo">Clan Docs</span>
  <nav>
    <div class={["menu", menuOpen && "open"]}>
      <button onclick={() => (menuOpen = !menuOpen)}>Menu</button>
      {@render navLinks(docs.navLinks)}
    </div>
  </nav>
</div>
<main>
  {@render children?.()}
</main>

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

<style>
  .global-bar {
    height: var(--globalBarHeight);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid;
    padding: 0 var(--pagePadding);
  }
  .menu > ul {
    visibility: hidden;
    position: fixed;
    left: 0;
    z-index: 10;
    top: var(--globalBarHeight);
    width: 100vw;
    height: 100vh;
    background: #fff;
  }
  .menu.open > ul {
    visibility: visible;
  }
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  li {
    padding-left: 1em;
  }
</style>
