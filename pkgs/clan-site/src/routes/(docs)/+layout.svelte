<script lang="ts">
  import type { ArticleInput } from "#lib/models/docs.ts";
  import { beforeNavigate } from "$app/navigation";
  import { Docs, setDocsContext } from "$lib/models/docs/docs.svelte.ts";
  import { page } from "$app/state";
  import TopBar from "~/lib/components/TopBar.svelte";

  const { data, children } = $props();
  // The warning is ignored because navItems themselves are never dynamically
  // updated, so we don't care about reactivity
  // svelte-ignore state_referenced_locally
  const docs = new Docs(data.navItems, () => page.data as ArticleInput);
  setDocsContext(docs);
  beforeNavigate(() => {
    window.scrollTo(0, 0);
  });
</script>

<div class="container" data-pagefind-body>
  <TopBar />
  <main
    class:showing-search={docs.search.results.length !== 0}
    data-page-id="docs"
  >
    {@render children?.()}
  </main>
</div>

<style>
  main {
    &.showing-search {
      display: none;
    }
  }

  @media (--medium) {
    .container {
      display: grid;
      grid-template: auto auto / 280px minmax(0, 1fr);
    }

    main {
      grid-row: 2;
      grid-column: 2;

      &.showing-search {
        display: block;
        overflow: hidden;
        max-block-size: calc(100vh - 60px);
      }
    }
  }
</style>
