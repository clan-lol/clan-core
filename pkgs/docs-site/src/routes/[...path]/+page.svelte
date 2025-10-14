<script lang="ts">
  import "$lib/markdown/main.css";
  import { visit, type Heading as ArticleHeading } from "$lib/docs";
  import { tick } from "svelte";
  const { data } = $props();

  type Heading = ArticleHeading & {
    scrolledPast: number;
    element: Element;
    children: Heading[];
  };

  const headings = $derived(normalizeHeadings(data.toc));
  let tocOpen = $state(false);
  let tocEl: HTMLElement;
  let tocLabelTextEl: HTMLElement;
  let tocLabelGhostEl: HTMLElement | null = $state(null);
  let tocLabelArrowEl: HTMLElement;
  let contentEl: HTMLElement;
  let currentHeading: Heading | null = $state(null);
  let previousHeading: Heading | null = $state(null);
  let animatingHeading = $state(true);
  let observer: IntersectionObserver | undefined;
  $effect(() => {
    data.content;
    observer?.disconnect();
    observer = new IntersectionObserver(onIntersectionChange, {
      threshold: 1,
      rootMargin: `${-(tocEl.offsetHeight + 2)}px 0 0`,
    });
    const els = contentEl.querySelectorAll("h1,h2,h3,h4,h5,h6");
    for (const el of els) {
      observer.observe(el);
    }
  });

  function normalizeHeadings(headings: ArticleHeading[]): Heading[] {
    return headings.map((heading) => ({
      ...heading,
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
    if (current?.id != currentHeading?.id) {
      if (current) {
        const animation = animateCurrentHeading(current, "toToc");
        await animation;
      } else {
        currentHeading = null;
      }
    }
  }

  async function animateCurrentHeading(
    heading: Heading,
    direction: "toToc" | "fromToc",
  ): Promise<void> {
    previousHeading = currentHeading;
    currentHeading = heading;
    const headingGhost = heading.element.cloneNode(true) as HTMLElement;
    const headingGhostInner = headingGhost.querySelector("&>span")!;
    headingGhost.classList.add("is-ghost");
    headingGhost.removeAttribute("id");
    headingGhost.style.top = `${tocEl.offsetHeight}px`;
    heading.element.parentNode!.insertBefore(headingGhost, heading.element);
    visit(headings, (heading) => {
      heading.element.classList.remove("is-current");
    });
    heading.element.classList.add("is-current");
    animatingHeading = true;
    await tick();
    const fromRect = headingGhostInner.getBoundingClientRect();
    const toRect = tocLabelTextEl.getBoundingClientRect();

    const headingGhostAnimation = headingGhostInner.animate(
      {
        transform: [
          `translate(0, 0) scale(1, 1)`,
          `translate(${toRect.left - fromRect.left}px, ${toRect.top - fromRect.top}px) scale(${toRect.width / fromRect.width}, ${toRect.height / fromRect.height})`,
        ],
        opacity: [1, 0],
      },
      {
        duration: 300,
        easing: "ease-out",
      },
    );
    const tocAnimation = tocLabelTextEl.animate(
      {
        transform: [
          `translate(${fromRect.left - toRect.left}px, ${fromRect.top - toRect.top}px) scale(${fromRect.width / toRect.width}, ${fromRect.height / toRect.height})`,
          `translate(0, 0) scale(1, 1)`,
        ],
        opacity: [0, 1],
      },
      {
        duration: 300,
        easing: "ease-out",
      },
    );
    tocLabelGhostEl = tocLabelGhostEl!;
    const tocGhostAnimation = tocLabelGhostEl.animate(
      { opacity: [1, 0] },
      { duration: 300 },
    );
    const tocGhostRect = tocLabelGhostEl.getBoundingClientRect();
    const tocArrowAnimation = tocLabelArrowEl.animate(
      {
        transform: [
          `translateX(${tocGhostRect.width - toRect.width}px)`,
          `translateX(0)`,
        ],
      },
      { duration: 300 },
    );
    await headingGhostAnimation.finished;
    headingGhost.remove();
    tocLabelGhostEl.remove();
    // const tocAnimation = tocLabelTextEl.animate(
    //   [
    //     {
    //       transform: `translate(${fromRect.left - toRect.left}px, ${fromRect.top - toRect.top}px) scale(${fromRect.width / toRect.width}, ${fromRect.height / toRect.height})`,
    //       opacity: 1,
    //     },
    //     {
    //       transform: `translate(0, 0) scale(1, 1)`,
    //       opacity: 1,
    //     },
    //   ],
    //   {
    //     duration: 20000,
    //   },
    // );
    // return {
    //   finished: headingAnimation.finished.then((animation) => {
    //     ghost.remove();
    //     return animation;
    //   }),
    //   cancel() {
    //     headingAnimation.cancel();
    //     // tocAnimation.cancel();
    //   },
    // };
  }

  function scrollToHeading(ev: Event, id: string) {
    ev.preventDefault();
    document.getElementById(id)?.scrollIntoView({
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
          {(!tocOpen && currentHeading?.content) || "Table of contents"}
        </span>
        {#if animatingHeading}
          <span class="toc-label-ghost" bind:this={tocLabelGhostEl}>
            {previousHeading?.content || "Table of contents"}
          </span>
        {/if}
        <span class="toc-label-arrow" bind:this={tocLabelArrowEl}>v</span>
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
        scrollToHeading(ev, heading.id);
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
    gap: 5px;
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
        &.is-current {
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
