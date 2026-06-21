<script lang="ts">
  import MobileTopBar from "./TopBar/MobileTopBar.svelte";
  import NavTree from "./TopBar/NavTree.svelte";
  import SearchResult from "./TopBar/SearchResult.svelte";
  import WideTopBar from "./TopBar/WideTopBar.svelte";
</script>

<MobileTopBar />
<div class="wide">
  <WideTopBar />
</div>
<NavTree />
<SearchResult />

<style>
  .wide {
    display: none;
  }

  @media (--docs-tablet) {
    .wide {
      display: contents;
    }
  }
</style>
