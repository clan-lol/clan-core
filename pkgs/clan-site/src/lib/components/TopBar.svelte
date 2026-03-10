<script lang="ts">
  import { getDocsContext } from "#lib/models/docs.ts";
  import NavBar from "./TopBar/NavBar.svelte";
  import NavTree from "./TopBar/NavTree.svelte";
  import SearchBar from "./TopBar/SearchBar.svelte";
  import SearchResult from "./TopBar/SearchResult.svelte";

  const docs = getDocsContext();
</script>

<header>
  <div class="inner" class:rotated={docs.topbarMode === "search"}>
    <NavBar />
    <SearchBar />
  </div>
</header>
<NavTree />
<SearchResult />

<style>
  header {
    perspective: 800px;
  }

  .inner {
    transition: 400ms;
    transform-origin: center center -30px;
    transform-style: preserve-3d;

    &.rotated {
      transform: rotateX(90deg);
    }
  }

  @media (--medium) {
    header {
      position: relative;
      z-index: 1001;
      grid-row: 1;
      grid-column: 1 / -1;
      perspective: none;
    }

    .inner {
      transition: none;
      transform: none;

      &.rotated {
        transform: none;
      }
    }
  }
</style>
