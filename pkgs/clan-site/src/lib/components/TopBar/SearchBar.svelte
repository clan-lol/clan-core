<script lang="ts">
  import { getDocsContext } from "$lib/models/docs.ts";
  import SearchIcon from "$lib/assets/icons/search.svg?component";

  const docs = getDocsContext();
</script>

<div class="container" class:rotated={docs.topbarMode === "search"}>
  <div class="inner">
    <form
      onsubmit={(ev): void => {
        ev.preventDefault();
      }}
    >
      <SearchIcon height="14" /><input
        bind:this={docs.search.inputElement}
        type="search"
        placeholder="Search"
        bind:value={docs.search.query}
      />
    </form>
    <button
      class="cancel"
      onclick={(): void => {
        docs.topbarMode = "topBar";
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
    background: color-mix(in srgb, var(--bg-color), #000 30%);
    transition: 400ms;
    transform: rotateX(-90deg);
    transform-origin: top center;

    &.rotated {
      background-color: var(--bg-color);
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
    background: #fff;
    border: #7b9b9f;
    border-radius: 999em;
    font-size: 16px;

    > input {
      flex: 1;
      block-size: 35px;
      margin-inline: 7px 12px;
      border: none;
      outline: none;
      font: inherit;
      font-size: inherit;

      &::placeholder {
        color: #4f747a;
      }
    }
  }

  .cancel {
    padding: 0 14px;
    background: transparent;
    border: 0;
    font: inherit;
    font-size: 14px;
  }

  @media (--medium) {
    .container {
      display: none;
      justify-content: center;
      transition: none;
      transform: none;

      &.rotated {
        display: flex;
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
    }

    .cancel {
      position: absolute;
      inset-inline-start: 100%;
    }
  }
</style>
