<script lang="ts">
  import * as config from "~/config";
  import "./index.css";

  import favicon from "$lib/assets/favicon.svg";
  import type { NavLink } from "./docs";

  const { data, children } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<nav>
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href={config.blog.base}>Blog</a></li>
    <li>
      <a href={config.docs.base}>Docs</a>
      {#if data.docs}{@render navLinks(data.docs.navLinks)}{/if}
    </li>
  </ul>
</nav>
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
  nav {
    height: var(--globalNavHeight);
    display: flex;
    align-items: center;
    border-bottom: 1px solid;
    padding: 0 var(--pagePadding);
  }
  ul {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;

    ul {
      display: none;
    }
  }
  li {
    padding-left: 2em;

    &:first-child {
      padding-left: 0;
    }
  }
</style>
