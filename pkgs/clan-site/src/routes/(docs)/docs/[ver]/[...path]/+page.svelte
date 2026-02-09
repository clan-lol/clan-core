<script lang="ts">
  /* eslint-disable svelte/no-unused-class-name */
  import { on } from "svelte/events";
  import { onMount } from "svelte";
  import { resolve } from "$app/paths";
  import "@clan/vite-plugin-markdown/main.css";

  const { data } = $props();
  const article = $derived(data.docsArticle);

  // TODO: add back for mobile
  // type Heading = ArticleHeading & {
  //   index: number;
  //   scrolledPast: number;
  //   element: Element;
  //   children: Heading[];
  // };
  //
  // let nextHeadingIndex = 0;
  // const headings = $derived(normalizeHeadings(article.toc));
  // let tocEl: HTMLElement;
  // let contentEl: HTMLElement;
  // let observer: IntersectionObserver | undefined;
  // let currentHeading: Heading | null = $state(null);
  // Let tocOpen = $state(false);
  // const defaultTocContent = "Table of contents";
  // const currentTocContent = $derived.by(() => {
  //   if (tocOpen) {
  //     return defaultTocContent;
  //   }
  //   return currentHeading?.content ?? defaultTocContent;
  // });
  //
  // $effect(() => {
  //   // Make sure the effect is triggered on content change
  //   // eslint-disable-next-line @typescript-eslint/no-unused-expressions
  //   article.content;
  //   observer?.disconnect();
  //   observer = new IntersectionObserver(
  //     (entries) => {
  //       // Record each heading's scrolledPast
  //       for (const entry of entries) {
  //         visit(headings, "children", (heading) => {
  //           if (heading.id !== entry.target.id) {
  //             return;
  //           }
  //           const {
  //             rootBounds,
  //             target,
  //             intersectionRatio,
  //             boundingClientRect,
  //           } = entry;
  //           if (!rootBounds) {
  //             return;
  //           }

  //           heading.element = target;
  //           heading.scrolledPast =
  //             intersectionRatio < 1 && boundingClientRect.top < rootBounds.top
  //               ? rootBounds.top - boundingClientRect.top
  //               : 0;
  //           return "break";
  //         });
  //       }
  //       let last: Heading | null = null;
  //       let current: Heading | null = null;
  //       // Find the last heading with scrolledPast > 0
  //       visit(headings, "children", (heading) => {
  //         if (last && last.scrolledPast > 0 && heading.scrolledPast === 0) {
  //           current = last;
  //           return "break";
  //         }
  //         last = heading;
  //         return;
  //       });
  //       currentHeading = current;
  //     },
  //     {
  //       threshold: 1,
  //       rootMargin: `${-tocEl.offsetHeight}px 0px 0px`,
  //     },
  //   );
  //   const els = contentEl.querySelectorAll("h1,h2,h3,h4,h5,h6");
  //   for (const el of els) {
  //     observer.observe(el);
  //   }
  // });

  onMount(() =>
    // Click tab to activate
    on(document, "click", (ev) => {
      const targetTabEl = (ev.target as HTMLElement).closest(".md-tabs-tab");
      if (!targetTabEl || targetTabEl.classList.contains(".is-active")) {
        return;
      }
      const tabsEl = targetTabEl.closest(".md-tabs");
      if (!tabsEl) {
        return;
      }
      const tabEls = tabsEl.querySelectorAll(".md-tabs-tab");
      const tabIndex = [...tabEls].indexOf(targetTabEl);
      if (tabIndex === -1) {
        return;
      }
      const tabContentEls = tabsEl.querySelectorAll(".md-tabs-content");
      const tabContentEl = tabContentEls[tabIndex];
      if (!tabContentEl) {
        return;
      }
      for (const tabEl of tabEls) {
        tabEl.classList.remove("is-active");
      }
      targetTabEl.classList.add("is-active");
      for (const tabContentEl of tabContentEls) {
        tabContentEl.classList.remove("is-active");
      }
      tabContentEl.classList.add("is-active");
    }),
  );

  // TODO: add back for mobile
  // function normalizeHeadings(headings: readonly ArticleHeading[]): Heading[] {
  //   // Use casting because the element property is supposed to be set by
  //   // svelte's bind: this
  //   const index = nextHeadingIndex;
  //   nextHeadingIndex += 1;
  //   return headings.map((heading) => ({
  //     ...heading,
  //     index,
  //     scrolledPast: 0,
  //     children: normalizeHeadings(heading.children),
  //   })) as Heading[];
  // }
  //
  // function scrollToHeading(ev: Event, headingEl: Element): void {
  //   ev.preventDefault();
  //   headingEl.scrollIntoView({
  //     behavior: "smooth",
  //   });
  //   tocOpen = false;
  // }
  // function scrollToTop(ev: Event): void {
  //   ev.preventDefault();
  //   window.scrollTo({
  //     top: 0,
  //     behavior: "smooth",
  //   });
  //   tocOpen = false;
  // }
</script>

<div>
  <!-- <div class="toc">
    <h2 bind:this={tocEl} class="toc-title">
      <button
        class="toc-label"
        onclick={() => {
          tocOpen = !tocOpen;
        }}
        type="button"
      >
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
    {#if tocOpen && headings[0]}
      {@const [heading] = headings}
      <ul class="toc-menu">
        <li>
          <a href={`#${heading.id}`} onclick={scrollToTop}>{heading.content}</a>
        </li>
        {@render tocLinks(heading.children)}
      </ul>
    {/if}
  </div> -->
  <div class="content">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html article.content}
  </div>
  <footer>
    {#if article.previous}
      <a class="pointer previous" href={resolve(article.previous.path)}>
        <div class="pointer-arrow">&lt;</div>
        <div>
          <div class="pointer-label">Previous</div>
          <div class="pointer-title">{article.previous.label}</div>
        </div>
      </a>
    {:else}
      <div class="pointer previous"></div>
    {/if}
    {#if article.next}
      <a class="pointer next" href={resolve(article.next.path)}>
        <div>
          <div class="pointer-label">Next</div>
          <div class="pointer-title">{article.next.label}</div>
        </div>
        <div class="pointer-arrow">&gt;</div>
      </a>
    {:else}
      <div class="pointer previous"></div>
    {/if}
  </footer>
</div>

<!-- {#snippet tocLinks(headings: Heading[])}
  {#each headings as heading (heading.id)}
    {@render tocLink(heading)}
  {/each}
{/snippet}

{#snippet tocLink(heading: Heading)}
  <li>
    <a
      href={`#${heading.id}`}
      onclick={(ev): void => {
        scrollToHeading(ev, heading.element);
      }}>{heading.content}</a
    >
    {#if heading.children.length !== 0}
      <ul>
        {@render tocLinks(heading.children)}
      </ul>
    {/if}
  </li>
{/snippet} -->

<style>
  .toc {
    position: sticky;
    top: 0;
    z-index: 1;

    h2 {
      margin: 0;
      padding: 15px 20px;
      background: #e5e5e5;
      font-weight: normal;
      font-size: 16px;
    }
  }

  button {
    padding: 0;
    border: 0;
    background: transparent;
    color: inherit;
    font: inherit;
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
    right: 0;
    left: 0;
    margin: 0;
    padding: 15px 20px;
    background: #fff;
    box-shadow: 0 3px 5px #00000020;
    list-style: none;

    ul {
      padding: 0 15px;
      list-style: none;
    }

    li {
      padding: 3px 0;
    }
  }

  .content {
    padding: 0 15px;

    :global {
      & :is(h1, h2, h3, h4, h5, h6) {
        display: flex;
        align-items: center;
        margin-left: -24px;

        &.is-scrolled-past {
          opacity: 0;
        }

        &.is-ghost {
          position: fixed;
          left: 0;
          z-index: 1;
          margin: 0;

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
    gap: 15px;
    justify-content: space-between;
    margin: 20px 15px;
  }

  .pointer {
    display: flex;
    flex: 1;
    gap: 10px;
    align-items: center;
    padding: 20px;
    border-radius: 8px;
    color: inherit;
    box-shadow: 0 2px 5px #00000030;
    text-decoration: none;
  }

  .pointer:empty {
    box-shadow: none;
  }

  .pointer.next {
    justify-content: end;
    text-align: right;
  }

  .pointer-title {
    font-size: 26px;
  }

  .pointer-label {
    font-size: 16px;
  }
</style>
