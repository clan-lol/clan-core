<script lang="ts">
  import "$lib/markdown/main.css";
  import { visit, type Heading as ArticleHeading } from "$lib/docs";
  import { onMount } from "svelte";
  const { data } = $props();

  type Heading = ArticleHeading & {
    index: number;
    scrolledPast: number;
    element: Element;
    children: Heading[];
  };

  let nextHeadingIndex = 0;
  const headings = $derived(normalizeHeadings(data.toc));
  let tocOpen = $state(false);
  let tocEl: HTMLElement;
  let contentEl: HTMLElement;
  let currentHeading: Heading | null = $state(null);
  let observer: IntersectionObserver | undefined;
  const defaultTocContent = "Table of contents";
  const currentTocContent = $derived.by(() => {
    if (tocOpen) {
      return defaultTocContent;
    }
    return currentHeading?.content || defaultTocContent;
  });

  $effect(() => {
    // Make sure the effect is triggered on content change
    data.content;
    observer?.disconnect();
    observer = new IntersectionObserver(onIntersectionChange, {
      threshold: 1,
      rootMargin: `${-tocEl.offsetHeight}px 0px 0px`,
    });
    const els = contentEl.querySelectorAll("h1,h2,h3,h4,h5,h6");
    for (const el of els) {
      observer.observe(el);
    }
  });

  onMount(() => {
    const onClick = (ev: MouseEvent) => {
      const targetTabEl = (ev.target as HTMLElement).closest(".md-tabs-tab");
      if (!targetTabEl || targetTabEl.classList.contains(".is-active")) {
        return;
      }
      const tabsEl = targetTabEl.closest(".md-tabs")!;
      const tabEls = tabsEl.querySelectorAll(".md-tabs-tab")!;
      const tabIndex = Array.from(tabEls).indexOf(targetTabEl);
      if (tabIndex == -1) {
        return;
      }
      const tabContentEls = tabsEl.querySelectorAll(".md-tabs-content");
      const tabContentEl = tabContentEls[tabIndex];
      if (!tabContentEl) {
        return;
      }
      tabEls.forEach((tabEl) => tabEl.classList.remove("is-active"));
      targetTabEl.classList.add("is-active");
      tabContentEls.forEach((tabContentEl) =>
        tabContentEl.classList.remove("is-active"),
      );
      tabContentEl.classList.add("is-active");
    };
    document.addEventListener("click", onClick);
    return () => {
      document.removeEventListener("click", onClick);
    };
  });

  function normalizeHeadings(headings: ArticleHeading[]): Heading[] {
    return headings.map((heading) => ({
      ...heading,
      index: nextHeadingIndex++,
      scrolledPast: 0,
      children: normalizeHeadings(heading.children),
    })) as Heading[];
  }

  async function onIntersectionChange(entries: IntersectionObserverEntry[]) {
    // Record each heading's scrolledPast
    for (const entry of entries) {
      visit(headings, (heading) => {
        if (heading.id != entry.target.id) {
          return;
        }
        heading.element = entry.target;
        heading.scrolledPast =
          entry.intersectionRatio < 1 &&
          entry.boundingClientRect.top < entry.rootBounds!.top
            ? entry.rootBounds!.top - entry.boundingClientRect.top
            : 0;
        return false;
      })!;
    }
    let last: Heading | null = null;
    let current: Heading | null = null;
    // Find the last heading with scrolledPast > 0
    visit(headings, (heading) => {
      if (last && last.scrolledPast > 0 && heading.scrolledPast === 0) {
        current = last;
        return false;
      }
      last = heading;
    });
    currentHeading = current;
  }

  function scrollToHeading(ev: Event, heading: Heading) {
    ev.preventDefault();
    heading.element.scrollIntoView({
      behavior: "smooth",
    });
    tocOpen = false;
  }
  function scrollToTop(ev: Event) {
    ev.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
    tocOpen = false;
  }
</script>

<div class="container">
  <div class="toc">
    <h2 class="toc-title" bind:this={tocEl}>
      <button class="toc-label" onclick={() => (tocOpen = !tocOpen)}>
        <span>
          {currentTocContent}
        </span>
        <svg
          fill="none"
          height="24"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          viewBox="0 0 24 24"
          width="18"
          xmlns="http://www.w3.org/2000/svg"
          ><polyline points="9 18 15 12 9 6" /></svg
        >
      </button>
    </h2>
    {#if tocOpen}
      <ul class="toc-menu">
        <li>
          <a href={`#${headings[0].id}`} onclick={scrollToTop}
            >{headings[0].content}</a
          >
        </li>
        {@render tocLinks(headings[0].children)}
      </ul>
    {/if}
  </div>
  <div class="content" bind:this={contentEl}>
    {@html data.content}
  </div>
  <footer>
    {#if data.frontmatter.previous}
      <a class="pointer previous" href={data.frontmatter.previous.link}>
        <div class="pointer-arrow">&lt;</div>
        <div>
          <div class="pointer-label">Previous</div>
          <div class="pointer-title">{data.frontmatter.previous.label}</div>
        </div>
      </a>
    {:else}
      <div class="pointer previous"></div>
    {/if}
    {#if data.frontmatter.next}
      <a class="pointer next" href={data.frontmatter.next.link}>
        <div>
          <div class="pointer-label">Next</div>
          <div class="pointer-title">{data.frontmatter.next.label}</div>
        </div>
        <div class="pointer-arrow">&gt;</div>
      </a>
    {:else}
      <div class="pointer previous"></div>
    {/if}
  </footer>
</div>

{#snippet tocLinks(headings: Heading[])}
  {#each headings as heading}
    {@render tocLink(heading)}
  {/each}
{/snippet}

{#snippet tocLink(heading: Heading)}
  <li>
    <a
      href={`#${heading.id}`}
      onclick={(ev) => {
        scrollToHeading(ev, heading);
      }}>{heading.content}</a
    >
    {#if heading.children.length != 0}
      <ul>
        {@render tocLinks(heading.children)}
      </ul>
    {/if}
  </li>
{/snippet}

<style>
  .toc {
    position: sticky;
    top: 0;
    z-index: 1;

    h2 {
      margin: 0;
      font-size: 16px;
      font-weight: normal;
      padding: 15px 20px;
      background: #e5e5e5;
    }
  }
  button {
    padding: 0;
    background: transparent;
    border: 0;
    font: inherit;
    color: inherit;
  }
  .toc-title {
    display: flex;
    justify-content: space-between;
  }
  .toc-label {
    display: flex;
    gap: 3px;
    align-items: center;
  }
  .toc-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin: 0;
    padding: 15px 20px;
    background: #fff;
    list-style: none;
    box-shadow: 0 3px 5px #00000020;

    ul {
      list-style: none;
      padding: 0 15px;
    }
    li {
      padding: 3px 0;
    }
  }
  .content {
    padding: 0 15px;
    width: 100vw;

    :global {
      & :is(h1, h2, h3, h4, h5, h6) {
        margin-left: calc(-1 * var(--pageMargin));
        display: flex;
        align-items: center;
        &.is-scrolledPast {
          opacity: 0;
        }
        &.is-ghost {
          position: fixed;
          z-index: 1;
          margin: 0;
          left: 0;

          > span {
            transform-origin: left top;
          }
        }
        a {
          text-decoration: none;
        }
        .icon {
          display: flex;
          align-items: center;
        }
        .icon::before {
          content: "🔗";
          font-size: 14px;
          visibility: hidden;
        }
        &:hover {
          .icon::before {
            visibility: visible;
          }
          &.is-ghost {
            .icon::before {
              visibility: hidden;
            }
          }
        }
      }
    }
  }

  footer {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    margin: 20px 15px;
  }
  .pointer {
    display: flex;
    align-items: center;
    flex: 1;
    box-shadow: 0 2px 5px #00000030;
    border-radius: 8px;
    padding: 20px;
    gap: 10px;
    text-decoration: none;
    color: inherit;
  }
  .pointer:empty {
    box-shadow: none;
  }
  .pointer.next {
    text-align: right;
    justify-content: end;
  }
  .pointer-title {
    font-size: 26px;
  }
  .pointer-label {
    font-size: 16px;
  }
</style>
