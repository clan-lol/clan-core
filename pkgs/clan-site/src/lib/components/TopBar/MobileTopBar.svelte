<script lang="ts">
  import { getDocsContext } from "#lib/models/docs.ts";
  import MobileSearchBar from "./MobileSearchBar.svelte";
  import { mount, onMount } from "svelte";
  import NavBar from "./NavBar.svelte";

  const docs = getDocsContext();
  let containerEl: HTMLElement;
  onMount(() => {
    mount(MobileSearchBar, {
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
    <MobileSearchBar />
  </div>
</header>

<style>
  header {
    position: relative;
    z-index: 1001;
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

  @media (--docs-tablet) {
    header {
      display: none;
    }
  }

  @media (--docs-top-bar-fixed) {
    header {
      position: sticky;
      inset-block-start: 0;
    }
  }
</style>
