<script lang="ts">
  import { getDocsContext } from "#lib/models/docs.ts";
  import MenuIcon from "$lib/assets/icons/menu.svg?component";

  const docs = getDocsContext();
</script>

<button
  title="Navigation"
  onclick={(): void => {
    docs.nav.toggle();
  }}><MenuIcon height="18" /></button
>

<style>
  button {
    padding: 0 14px;
    margin-inline-end: -14px;
    color: inherit;
    background: none;
    border: 0;
    cursor: pointer;
  }

  @media (--medium) {
    button {
      display: none;
    }
  }
</style>
