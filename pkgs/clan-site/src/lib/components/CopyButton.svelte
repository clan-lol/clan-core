<script lang="ts">
  import { copyButtonMessageDelay } from "$config";
  import CopyFilledIcon from "$lib/assets/icons/copy-filled.svg?component";
  import CopyIcon from "$lib/assets/icons/copy.svg?component";
  import { sleep } from "$lib/util.ts";

  let showingMessage = $state(false);

  let controller: AbortController | undefined;
  function onClick(ev: MouseEvent): void {
    const el = (ev.target as HTMLElement)
      .closest("pre.shiki")
      ?.querySelector("code");
    if (!el) {
      return;
    }
    controller?.abort();
    controller = new AbortController();

    (async (): Promise<void> => {
      await globalThis.navigator.clipboard.writeText(el.textContent);
      showingMessage = true;
      try {
        await sleep(copyButtonMessageDelay, { signal: controller.signal });
        showingMessage = false;
      } catch {
        // Ignore cancel error
      }
    })();
  }
</script>

<button
  onclick={onClick}
  onmouseleave={(): void => {
    showingMessage = false;
  }}
  >{#if showingMessage}<CopyFilledIcon height="20" /><span>Copied</span
    >{:else}<CopyIcon height="20" />{/if}</button
>

<style>
  button {
    position: absolute;
    inset-inline-end: 6px;
    inset-block-start: 6px;
    display: none;
    gap: 8px;
    padding: 8px;
    color: var(--code-copy-button-fg-color);
    background: var(--code-copy-button-bg-color);
    border: 0;
    border-radius: 5px;
    cursor: pointer;

    :global(pre.shiki):hover & {
      display: flex;
    }

    :global(svg) {
      display: block;
    }
  }

  span {
    display: flex;
    align-items: center;
    order: -1;
    font-size: 14px;
  }
</style>
