<script lang="ts">
  import { getDocsContext } from "$lib/models/docs.ts";
  import SearchIcon from "$lib/assets/icons/search.svg?component";

  const { double = false }: { double?: boolean } = $props();
  const docs = getDocsContext();
</script>

<div
  class="container"
  class:double
  class:real={!double}
  class:rotated={docs.topbarMode === "search"}
>
  <div class="inner">
    <form
      onsubmit={(ev): void => {
        ev.preventDefault();
      }}
    >
      <SearchIcon height="14" /><input
        bind:this={
          (): HTMLInputElement =>
            double ? docs.search.inputDoubleElement : docs.search.inputElement,
          (el): void => {
            if (double) {
              docs.search.inputDoubleElement = el;
            } else {
              docs.search.inputElement = el;
            }
          }
        }
        type="search"
        placeholder="Search"
        bind:value={docs.search.query}
      />
    </form>
    <button
      class="cancel"
      onclick={(): void => {
        docs.topbarMode = "navBar";
      }}>Cancel</button
    >
  </div>
</div>

<style>
  .container {
    position: absolute;
    inset-inline: 0;
    display: flex;
    block-size: 60px;

    &.real {
      background: color-mix(in srgb, var(--bg-color), #000 30%);
      transition: var(--top-bar-toggle-duration);
      transform: rotateX(-90deg);
      transform-origin: top center;

      &.rotated {
        background-color: var(--bg-color);
      }
    }

    &.double {
      inset-block-start: 0;
      opacity: 0;
      pointer-events: none;
      transition: 0ms var(--top-bar-toggle-duration);

      &.rotated {
        opacity: 1;
      }
    }
  }

  .inner {
    display: flex;
    flex: 1;
    align-items: center;
  }

  form {
    display: flex;
    flex: 1;
    align-items: center;
    padding-inline-start: 11px;
    margin-inline-start: 14px;
    border-radius: 999em;
    font-size: 16px;

    .real & {
      background: var(--search-input-bg-color);
    }

    .double & {
      :global(svg) {
        visibility: hidden;
      }
    }

    > input {
      flex: 1;
      block-size: 35px;
      padding: 0;
      margin-inline: 7px 12px;
      background: transparent;
      border: none;
      outline: none;
      font: inherit;
      font-size: inherit;

      .real & {
        color: transparent;

        &::placeholder {
          color: var(--search-input-placeholder-color);
        }
      }

      .double & {
        pointer-events: all;

        &::placeholder {
          color: transparent;
        }

        &::-webkit-search-cancel-button {
          opacity: 0;
        }
      }
    }
  }

  .cancel {
    padding: 0 14px;
    color: inherit;
    background: transparent;
    border: 0;
    font: inherit;
    font-size: 14px;

    .double & {
      visibility: hidden;
    }
  }

  @media (--medium) {
    .container {
      display: none;
      justify-content: center;

      &.rotated {
        display: flex;
      }

      &.real {
        transition: none;
        transform: none;
      }

      &.double {
        display: none;
      }
    }

    .inner {
      position: relative;
      flex: 0 1 auto;
    }

    form {
      flex: none;
      inline-size: 400px;
      margin-inline-start: 0;

      > input {
        .real & {
          color: inherit;
        }
      }
    }

    .cancel {
      position: absolute;
      inset-inline-start: 100%;
    }
  }
</style>
