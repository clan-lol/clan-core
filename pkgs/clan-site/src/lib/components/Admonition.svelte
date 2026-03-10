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
    class:is-info={type === "info"}
    class:is-example={type === "example"}
    class:is-warning={type === "warning"}
    class:is-developer={type === "developer"}
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
    class:is-info={type === "info"}
    class:is-example={type === "example"}
    class:is-warning={type === "warning"}
    class:is-developer={type === "developer"}
  >
    <dt><Icon height="18" />{title}</dt>
    <dd>{@render children?.()}</dd>
  </dl>
{/if}

<style>
  dl,
  details {
    padding: 0 1rem;
    margin: 1rem 0;
    border-inline-start: 4px solid;
    border-block-start: 1px solid transparent;
    border-block-end: 1px solid transparent;

    &.is-note {
      background-color: var(--admonition-note-bg-color);
      border-inline-start-color: var(--admonition-note-border-color);
    }

    &.is-important {
      background-color: var(--admonition-important-bg-color);
      border-inline-start-color: var(--admonition-important-border-color);
    }

    &.is-danger {
      background-color: var(--admonition-danger-bg-color);
      border-inline-start-color: var(--admonition-danger-border-color);
    }

    &.is-tip {
      background-color: var(--admonition-tip-bg-color);
      border-inline-start-color: var(--admonition-tip-border-color);
    }

    &.is-info {
      background-color: var(--admonition-info-bg-color);
      border-inline-start-color: var(--admonition-info-border-color);
    }

    &.is-example {
      background-color: var(--admonition-example-bg-color);
      border-inline-start-color: var(--admonition-example-border-color);
    }

    &.is-warning {
      background-color: var(--admonition-warning-bg-color);
      border-inline-start-color: var(--admonition-warning-border-color);
    }

    &.is-developer {
      background-color: var(--admonition-developer-bg-color);
      border-inline-start-color: var(--admonition-developer-border-color);
    }
  }

  dt,
  summary {
    display: flex;
    gap: 0.5rem;
    justify-content: start;
    align-items: center;
    margin: 1em 0;
    font-weight: 600;
    text-transform: capitalize;

    :global(svg) {
      flex: none;
    }

    .is-note > & {
      color: var(--admonition-note-fg-color);
    }

    .is-important > & {
      color: var(--admonition-important-fg-color);
    }

    .is-danger > & {
      color: var(--admonition-danger-fg-color);
    }

    .is-tip > & {
      color: var(--admonition-tip-fg-color);
    }

    .is-info > & {
      color: var(--admonition-info-fg-color);
    }

    .is-example > & {
      color: var(--admonition-example-fg-color);
    }

    .is-warning > & {
      color: var(--admonition-warning-fg-color);
    }

    .is-developer > & {
      color: var(--admonition-developer-fg-color);
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
