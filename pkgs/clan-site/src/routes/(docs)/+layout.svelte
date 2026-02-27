<script lang="ts">
  import type { ArticleInput } from "#lib/models/docs.ts";
  import { Docs, setDocsContext } from "$lib/models/docs/docs.svelte.ts";
  import Masthead from "$lib/components/Masthead.svelte";
  import Nav from "$lib/components/Nav.svelte";
  import { onNavigate } from "$app/navigation";
  import { page } from "$app/state";
  import Search from "$lib/components/Search.svelte";

  const { data, children } = $props();
  // The warning is ignored because navItems themselves are never dynamically
  // updated, so we don't care about reactivity
  // svelte-ignore state_referenced_locally
  const docs = new Docs(data.navItems, () => page.data as ArticleInput);
  setDocsContext(docs);
  onNavigate(() => {
    window.scrollTo(0, 0);
  });
</script>

<Masthead />
<Search />
<main data-page-id="docs">
  <aside>
    <Nav />
  </aside>
  {@render children?.()}
</main>

<style>
  @media (--medium) {
    main {
      display: flex;
    }
  }
</style>
