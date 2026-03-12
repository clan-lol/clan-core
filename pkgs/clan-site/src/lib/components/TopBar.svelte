<script lang="ts">
  import { getDocsContext } from "#lib/models/docs.ts";
  import { mount, onMount } from "svelte";
  import NavBar from "./TopBar/NavBar.svelte";
  import NavTree from "./TopBar/NavTree.svelte";
  import SearchBar from "./TopBar/SearchBar.svelte";
  import SearchResult from "./TopBar/SearchResult.svelte";

  const docs = getDocsContext();
  let containerEl: HTMLElement;
  onMount(() => {
    mount(SearchBar, {
      target: containerEl,
      props: {
        double: true,
      },
    });
  });
</script>

<header class:rotated={docs.topbarMode === "search"} bind:this={containerEl}>
  <div class="inner">
    <NavBar />
    <SearchBar />
  </div>
</header>
<NavTree />
<SearchResult />

<style>
  header {
    position: sticky;
    inset-block-start: 0;
    z-index: 1000;
    perspective: 800px;
  }

  .inner {
    transition: var(--top-bar-toggle-duration);
    transform-origin: center center -30px;
    transform-style: preserve-3d;

    .rotated & {
      transform: rotateX(90deg);
    }
  }

  @media (--medium) {
    header {
      position: sticky;
      inset-block-start: 0;
      z-index: 1001;
      grid-row: 1;
      grid-column: 1 / -1;
      perspective: none;
    }

    .inner {
      transition: none;
    }
  }
</style>
