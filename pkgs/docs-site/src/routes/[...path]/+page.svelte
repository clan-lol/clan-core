<script lang="ts">
  import "$lib/markdown/main.css";
  import { visit, type Heading as ArticleHeading } from "$lib/docs";
  import { tick } from "svelte";
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
  let tocLabelTextEl: HTMLElement;
  let tocLabelGhostEl: HTMLElement | null = $state(null);
  let tocLabelArrowEl: HTMLElement;
  let contentEl: HTMLElement;
  let currentHeading: Heading | null = $state(null);
  let previousHeading: Heading | null = $state(null);
  let isTocAnimating: "toToc" | "fromToc" | false = $state(false);
  let observer: IntersectionObserver | undefined;
  const defaultTocContent = "Table of contents";
  const currentTocContent = $derived.by(() => {
    if (tocOpen) {
      return defaultTocContent;
    }
    if (isTocAnimating == "toToc") {
      return currentHeading!.content;
    }
    if (isTocAnimating == "fromToc") {
      return previousHeading!.content;
    }
    return currentHeading?.content || defaultTocContent;
  });
  const ghostTocContent = $derived.by(() => {
    if (isTocAnimating == "toToc") {
      return previousHeading?.content || defaultTocContent;
    }
    return currentHeading?.content || defaultTocContent;
  });

  $effect(() => {
    // Make sure the effect is triggered on content change
    data.content;
    observer?.disconnect();
    observer = new IntersectionObserver(onIntersectionChange, {
      threshold: 1,
      rootMargin: `${-tocEl.offsetHeight}px 0 0`,
    });
    const els = contentEl.querySelectorAll("h1,h2,h3,h4,h5,h6");
    for (const el of els) {
      observer.observe(el);
    }
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
    current = current as Heading | null;
    let controller: AbortController | undefined;
    if (current?.id != currentHeading?.id) {
      previousHeading = currentHeading;
      currentHeading = current;
      controller?.abort();
      controller = new AbortController();
      await animateCurrentHeading({ signal: controller.signal });
    }
  }

  async function animateCurrentHeading({
    signal,
  }: {
    signal: AbortSignal;
  }): Promise<void> {
    let animatingHeading: Heading;
    if (!previousHeading) {
      // Impossible situation
      if (!currentHeading) return;
      isTocAnimating = "toToc";
    } else if (!currentHeading) {
      isTocAnimating = "fromToc";
    } else {
      isTocAnimating =
        currentHeading.index > previousHeading.index ? "toToc" : "fromToc";
    }
    if (isTocAnimating == "toToc") {
      animatingHeading = currentHeading!;
      currentHeading!.element.classList.add("is-scrolledPast");
    } else {
      animatingHeading = previousHeading!;
    }
    const ghostHeadingEl = animatingHeading.element.cloneNode(
      true,
    ) as HTMLElement;
    const ghostHeadingInnerEl = ghostHeadingEl.querySelector("&>span")!;
    ghostHeadingEl.classList.add("is-ghost");
    ghostHeadingEl.classList.remove("is-scrolledPast");
    ghostHeadingEl.removeAttribute("id");
    ghostHeadingEl.style.top = `${isTocAnimating == "toToc" ? tocEl.offsetHeight : animatingHeading.element.getBoundingClientRect().top}px`;
    animatingHeading.element.parentNode!.insertBefore(
      ghostHeadingEl,
      animatingHeading.element,
    );
    await tick();
    const headingRect = ghostHeadingInnerEl.getBoundingClientRect();
    const tocRect = tocLabelTextEl.getBoundingClientRect();

    const ghostHeadingAnimation = ghostHeadingInnerEl.animate(
      {
        transform:
          isTocAnimating == "toToc"
            ? [
                `translate(0, 0) scale(1, 1)`,
                `translate(${tocRect.left - headingRect.left}px, ${tocRect.top - headingRect.top}px) scale(${tocRect.width / headingRect.width}, ${tocRect.height / headingRect.height})`,
              ]
            : [
                `translate(${tocRect.left - headingRect.left}px, ${tocRect.top - headingRect.top}px) scale(${tocRect.width / headingRect.width}, ${tocRect.height / headingRect.height})`,
                `translate(0, 0) scale(1, 1)`,
              ],
        opacity: [1, 0],
      },
      {
        duration: 250,
        easing: "ease-out",
      },
    );
    const tocAnimation = tocLabelTextEl.animate(
      {
        transform:
          isTocAnimating == "toToc"
            ? [
                `translate(${headingRect.left - tocRect.left}px, ${headingRect.top - tocRect.top}px) scale(${headingRect.width / tocRect.width}, ${headingRect.height / tocRect.height})`,
                `translate(0, 0) scale(1, 1)`,
              ]
            : [
                `translate(0, 0) scale(1, 1)`,
                `translate(${headingRect.left - tocRect.left}px, ${headingRect.top - tocRect.top}px) scale(${headingRect.width / tocRect.width}, ${headingRect.height / tocRect.height})`,
              ],
        opacity: [0, 1],
      },
      {
        duration: 250,
        easing: "ease-out",
      },
    );
    tocLabelGhostEl = tocLabelGhostEl!;
    const tocGhostAnimation = tocLabelGhostEl.animate(
      { opacity: isTocAnimating == "toToc" ? [1, 0] : [0, 1] },
      { duration: 250 },
    );
    const tocGhostRect = tocLabelGhostEl.getBoundingClientRect();
    const tocArrowAnimation = tocLabelArrowEl.animate(
      {
        transform:
          isTocAnimating == "toToc"
            ? [
                `translateX(${tocGhostRect.width - tocRect.width}px)`,
                `translateX(0)`,
              ]
            : [
                `translateX(0)`,
                `translateX(${tocGhostRect.width - tocRect.width}px)`,
              ],
      },
      { duration: 250 },
    );
    signal.addEventListener("abort", () => {
      tocAnimation.cancel();
      tocGhostAnimation.cancel();
      tocArrowAnimation.cancel();
    });
    await ghostHeadingAnimation.finished;
    if (isTocAnimating == "fromToc") {
      previousHeading!.element.classList.remove("is-scrolledPast");
    }
    ghostHeadingEl.remove();
    tocLabelGhostEl.remove();
    isTocAnimating = false;
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
        <span class="toc-label-text" bind:this={tocLabelTextEl}>
          {currentTocContent}
        </span>
        {#if isTocAnimating}
          <span class="toc-label-ghost" bind:this={tocLabelGhostEl}>
            {ghostTocContent}
          </span>
        {/if}
        <svg
          class="toc-label-arrow"
          bind:this={tocLabelArrowEl}
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
  .toc-label-text,
  .toc-label-ghost {
    transform-origin: left top;
  }
  .toc-label-ghost {
    position: absolute;
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
        margin-left: calc(-1 * var(--pagePadding));
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
