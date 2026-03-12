<script lang="ts">
  import { Docs } from "#lib/models/docs.ts";
  import { docsBase, version } from "$config";
  import { onMount } from "svelte";
  import { resolve } from "$app/paths";

  let vers: string[] = $state.raw([]);
  let showingVers = $state(false);
  onMount(() => {
    (async (): Promise<void> => {
      vers = await Docs.getVersions();
    })();
  });
</script>

<svelte:document
  onclick={(): void => {
    showingVers = false;
  }}
/>

<article>
  <button
    onclick={(ev): void => {
      ev.stopPropagation();
      showingVers = !showingVers;
    }}>{version}</button
  >
  {#if showingVers}
    <ol>
      {#if vers.length === 0}
        <li></li>
      {:else}
        {#each vers as ver (ver)}
          {#if ver !== version}
            <li>
              <!-- Docs actually ignores the version after /docs, for the
              version switcher to actually load a different version of Docs, a
              full page reload must be forced -->
              <a data-sveltekit-reload href={resolve(`${docsBase}/${ver}`)}
                >{ver}</a
              >
            </li>
          {/if}
        {/each}
      {/if}
    </ol>
  {/if}
</article>

<style>
  article {
    position: relative;
  }

  button {
    padding: 6px 8px;
    color: var(--content-fg-color);
    background: var(--content-bg-color);
    border: 0;
    border-radius: 5px;
    font-weight: 500;
    font-size: 14px;
    cursor: pointer;
  }

  ol {
    position: absolute;
    inset-inline-start: 0;
    inset-block-start: 100%;
    min-inline-size: 100%;
    padding: 0;
    margin: 0;
    margin-block-start: 1px;
    color: var(--content-fg-color);
    background: var(--content-bg-color);
    border-radius: 5px;
    list-style: none;
  }

  a {
    display: block;
    padding: 6px 8px;
    color: inherit;
    text-decoration: none;
  }
</style>
