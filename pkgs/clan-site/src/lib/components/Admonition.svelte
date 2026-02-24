<script lang="ts">
  import type { AdmonitionType } from "@clan.lol/svelte-md";
  import type { Snippet } from "svelte";
  import ChevronRightIcon from "$lib/assets/icons/chevron-right.svg?component";
  import DangerIcon from "$lib/assets/icons/warning-filled.svg?component";
  import ImportantIcon from "$lib/assets/icons/attention.svg?component";
  import NoteIcon from "$lib/assets/icons/info.svg?component";
  import TipIcon from "$lib/assets/icons/heart.svg?component";

  const defaultTitle = {
    note: "Note",
    important: "Important",
    danger: "Danger",
    tip: "Tip",
  };

  const {
    type,
    title = defaultTitle[type],
    collapsed,
    children,
  }: {
    type: AdmonitionType;
    title?: string;
    collapsed?: boolean;
    children: Snippet;
  } = $props();

  const Icon = $derived(
    {
      note: NoteIcon,
      important: ImportantIcon,
      danger: DangerIcon,
      tip: TipIcon,
    }[type],
  );
</script>

{#if collapsed}
  <details
    class:is-note={type === "note"}
    class:is-important={type === "important"}
    class:is-danger={type === "danger"}
    class:is-tip={type === "tip"}
  >
    <summary
      ><Icon height="18" />{title}<ChevronRightIcon height="18" /></summary
    >
    <div>{@render children()}</div>
  </details>
{:else}
  <dl
    class:is-note={type === "note"}
    class:is-important={type === "important"}
    class:is-danger={type === "danger"}
    class:is-tip={type === "tip"}
  >
    <dt><Icon height="18" />{title}</dt>
    <dd>{@render children()}</dd>
  </dl>
{/if}

<style>
  dl,
  details {
    padding: 1rem;
    margin: 1rem 0;
    border-inline-start: 4px solid;

    &.is-note {
      background-color: #eff6ff;
      border-inline-start-color: #3b82f6;
    }

    &.is-important {
      background-color: #fffbeb;
      border-inline-start-color: #facc15;
    }

    &.is-danger {
      background-color: #fef2f2;
      border-inline-start-color: #ef4444;
    }

    &.is-tip {
      background-color: #ecfdf5;
      border-inline-start-color: #10b981;
    }
  }

  dt,
  summary {
    display: flex;
    gap: 0.5rem;
    justify-content: start;
    align-items: center;
    font-weight: 600;
    text-transform: capitalize;

    .is-note > & {
      color: #1e40af;
    }

    .is-important > & {
      color: #b45309;
    }

    .is-danger > & {
      color: #b91c1c;
    }

    .is-tip > & {
      color: #065f46;
    }
  }

  summary {
    position: relative;

    :global(svg:last-child) {
      position: absolute;
      inset-inline-end: 0;
      transition: 200ms;
    }

    details[open] & :global(svg:last-child) {
      transform: rotate(90deg);
    }
  }
</style>
