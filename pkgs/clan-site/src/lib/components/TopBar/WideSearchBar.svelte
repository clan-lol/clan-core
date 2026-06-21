<script lang="ts">
  import { getDocsContext } from "$lib/models/docs.ts";
  import SearchIcon from "$lib/assets/icons/search.svg?component";

  const docs = getDocsContext();
  const isFocused = $derived(docs.topbarMode === "search");
  let isAnimating = $state(false);

  function showSearch(): void {
    isAnimating = true;
    docs.topbarMode = "search";
  }

  function hideSearch(): void {
    isAnimating = true;
    docs.topbarMode = "navBar";
  }
</script>

<article
  class:is-focused={isFocused}
  class:is-animating={isAnimating}
  ontransitionend={(ev): void => {
    if (ev.target === ev.currentTarget && ev.propertyName === "transform") {
      isAnimating = false;
    }
  }}
>
  <form
    onsubmit={(ev): void => {
      ev.preventDefault();
    }}
  >
    <label>
      <SearchIcon height="16" />
      <input
        bind:this={
          (): HTMLInputElement | undefined => docs.search.inputElement,
          (el): void => {
            docs.search.inputElement = el;
          }
        }
        type="search"
        placeholder="Search"
        bind:value={docs.search.query}
        onfocus={showSearch}
        onkeydown={(ev): void => {
          if (ev.key === "Escape") {
            hideSearch();
          }
        }}
      />
    </label>
  </form>
  <button class="cancel" type="button" onclick={hideSearch}>Cancel</button>
</article>

<style>
  article {
    position: relative;
    display: flex;
    pointer-events: none;
    transform: translateX(calc(50vw - var(--docs-gutter-inline-end) - 110px));

    &.is-animating {
      transition: transform 250ms ease;
    }

    &.is-focused {
      transform: translateX(0);
    }
  }

  form {
    display: flex;
    inline-size: 220px;
    block-size: 35px;
    padding-inline-start: 11px;
    color: var(--search-fg-color);
    background: transparent;
    border: 1px solid var(--search-border-color);
    border-radius: 999em;
    pointer-events: auto;

    .is-animating & {
      transition:
        inline-size 250ms ease,
        color 250ms ease,
        background-color 250ms ease,
        border-color 250ms ease;
    }

    .is-focused & {
      inline-size: 400px;
      color: inherit;
      background: var(--search-input-bg-color);
      border-color: transparent;
    }
  }

  label {
    display: flex;
    gap: 5px;
    align-items: center;
    inline-size: 100%;
    block-size: 100%;
    cursor: text;
  }

  input {
    flex: 1;
    min-inline-size: 0;
    block-size: 100%;
    padding: 0;
    margin-inline-end: 12px;
    color: inherit;
    background: transparent;
    border: none;
    outline: none;
    font: inherit;
    font-size: 14px;

    &::placeholder {
      color: currentcolor;
    }

    .is-focused &::placeholder {
      color: var(--search-input-placeholder-color);
    }
  }

  .cancel {
    position: absolute;
    inset-inline-start: calc(100% + 10px);
    inset-block: 0;
    padding: 0 14px;
    color: inherit;
    background: transparent;
    border: 0;
    font: inherit;
    font-size: 14px;
    opacity: 0;
    visibility: hidden;

    .is-animating & {
      transition:
        opacity 250ms ease,
        visibility 0ms 250ms;
    }

    .is-focused & {
      opacity: 1;
      visibility: visible;
    }

    .is-animating.is-focused & {
      transition: opacity 250ms ease;
    }
  }
</style>
