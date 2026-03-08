<script lang="ts">
  import type { AdmonitionType } from "@clan.lol/svelte-md";
  import type { Snippet } from "svelte";
  import ChevronRightIcon from "$lib/assets/icons/chevron-right.svg?component";
  import EditIcon from "$lib/assets/icons/edit.svg?component";
  import ImportantIcon from "$lib/assets/icons/attention.svg?component";
  import InfoIcon from "$lib/assets/icons/info.svg?component";
  import TipIcon from "$lib/assets/icons/heart.svg?component";
  import WarningIcon from "$lib/assets/icons/warning-filled.svg?component";

  const defaultTitle = {
    info: "Info",
    note: "Note",
    important: "Important",
    danger: "Danger",
    tip: "Tip",
    example: "Example",
    warning: "Warning",
    developer: "Developer",
  };

  let {
    type,
    title = defaultTitle[type],
    collapsible,
    open = $bindable(),
    children,
  }: {
    type: AdmonitionType;
    title?: string;
    collapsible?: boolean;
    open?: boolean;
    children?: Snippet;
  } = $props();

  const Icon = $derived(
    {
      info: InfoIcon,
      note: InfoIcon,
      important: ImportantIcon,
      danger: WarningIcon,
      tip: TipIcon,
      example: WarningIcon,
      warning: WarningIcon,
      developer: EditIcon,
    }[type],
  );
</script>

{#if collapsible}
  <details
    bind:open
    class:is-note={type === "note"}
    class:is-important={type === "important"}
    class:is-danger={type === "danger"}
    class:is-tip={type === "tip"}
  >
    <summary
      ><Icon height="18" />{title}<ChevronRightIcon height="18" /></summary
    >
    <div class="content">{@render children?.()}</div>
  </details>
{:else}
  <dl
    class:is-note={type === "note"}
    class:is-important={type === "important"}
    class:is-danger={type === "danger"}
    class:is-tip={type === "tip"}
  >
    <dt><Icon height="18" />{title}</dt>
    <dd>{@render children?.()}</dd>
  </dl>
{/if}

<style>
  dl,
  details {
    padding: 1rem;
    margin: 1rem 0;
    border-inline-start: 4px solid;

    &.is-note {
      background-color: var(--admonition-note-bg);
      border-inline-start-color: var(--admonition-note-border);
    }

    &.is-important {
      background-color: var(--admonition-important-bg);
      border-inline-start-color: var(--admonition-important-border);
    }

    &.is-danger {
      background-color: var(--admonition-danger-bg);
      border-inline-start-color: var(--admonition-danger-border);
    }

    &.is-tip {
      background-color: var(--admonition-tip-bg);
      border-inline-start-color: var(--admonition-tip-border);
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
      color: var(--admonition-note-fg);
    }

    .is-important > & {
      color: var(--admonition-important-fg);
    }

    .is-danger > & {
      color: var(--admonition-danger-fg);
    }

    .is-tip > & {
      color: var(--admonition-tip-fg);
    }
  }

  dd,
  .content {
    font-size: 16px;
  }

  dd {
    margin: 0;
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
