<script lang="ts">
  import type { AdmonitionType } from "../../../packages/md-svelte/index.ts";
  import type { Snippet } from "svelte";
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
    children,
  }: {
    type: AdmonitionType;
    title?: string;
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

<dl
  class:is-note={type === "note"}
  class:is-important={type === "important"}
  class:is-danger={type === "danger"}
  class:is-tip={type === "tip"}
>
  <dt>
    <Icon height="18" />{title}
  </dt>
  <dd>{@render children()}</dd>
</dl>

<style>
  dl {
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

  dt {
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
</style>
