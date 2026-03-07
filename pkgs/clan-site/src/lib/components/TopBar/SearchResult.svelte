<script lang="ts">
  import { getDocsContext } from "$lib/models/docs.ts";

  const docs = getDocsContext();
</script>

{#if docs.search.results.length !== 0}
  <dl>
    {#each docs.search.results as result (result)}
      <div class="search-result">
        <dt>
          <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
          <a href={result.url.slice(0, -".html".length)}
            >{result.meta["title"]}</a
          >
        </dt>

        <dd>
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          {@html result.excerpt}
        </dd>
      </div>
    {/each}
  </dl>
{/if}

<style>
  dl {
    position: absolute;
    inset-inline: 0;
    inset-block: 60px 0;
    overflow: auto;
    margin: 0;
    background: #fff;
  }

  dd {
    margin: 0;
    margin-block-start: 1em;
    font-size: 16px;
  }

  .search-result {
    padding: 14px;
    border-block-end: 1px solid var(--search-result-separator-color);
  }

  @media (--medium) {
    dl {
      inset-inline-start: calc(50% - 325px);
      inline-size: 650px;
      max-block-size: 80vh;
      border-end-start-radius: 12px;
      border-end-end-radius: 12px;
      box-shadow: 0 8px 24px #00000030;
    }

    .search-result {
      padding: 14px 24px;
    }
  }
</style>
