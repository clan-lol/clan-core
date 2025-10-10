<script lang="ts">
  import "$lib/markdown/main.css";
  import { onMount } from "svelte";
  import { visitHeadings, type Heading } from "$lib/docs";
  import { browser } from "$app/environment";
  const { data } = $props();
  const toc = $state(data.toc);
  let tocOpen = $state(false);

  let tocEl: HTMLElement;
  let tocLabelTextEl: HTMLElement;
  let currentHeading = $derived.by(() => {
    if (!browser) {
      return null;
    }
    let last: Heading | null = null;
    let current: Heading | null = null;
    // This can run before the IntersectionObserver runs, where element is
    // still not available
    visitHeadings(toc, (heading) => {
      if (!heading.element?.classList.contains("current")) {
        return;
      }
      heading.element.classList.remove("current");
    });
    let headingAnimation: Animation | undefined;
    let tocAnimation: Animation | undefined;
    visitHeadings(toc, (heading) => {
      if (last && last.scrolledPast > 0 && heading.scrolledPast === 0) {
        headingAnimation?.cancel();
        tocAnimation?.cancel();
        current = last;
        // let ghost: HTMLElement;
        // ({ ghost, headingAnimation, tocAnimation } = animateHeading(
        //   current.element,
        //   "toToc",
        // ));
        current.element.classList.add("current");
        // headingAnimation.finished.then(() => ghost.remove());
        return false;
      }
      last = heading;
    });
    return current;
  }) as Heading | null;

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          visitHeadings(toc, (heading) => {
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
      },
      {
        threshold: 1,
        rootMargin: `${-(tocEl.offsetHeight + 2)}px 0 0`,
      },
    );
    const headings = document.querySelectorAll(
      ".content h1, .content h2, .content h3",
    );
    for (const heading of headings) {
      observer.observe(heading);
    }
  });

  function animateHeading(
    heading: Element,
    direction: "toToc" | "fromToc",
  ): {
    ghost: HTMLElement;
    headingAnimation: Animation;
    tocAnimation: Animation;
  } {
    const ghost = heading.cloneNode(true) as HTMLElement;
    const ghostInner = heading.querySelector("&>span")!;
    const fromRect = ghostInner.getBoundingClientRect();
    const toRect = tocLabelTextEl.getBoundingClientRect();
    ghost.classList.add("heading-ghost");
    heading.parentNode!.insertBefore(ghost, heading.nextSibling);
    const headingAnimation = ghostInner.animate(
      [
        {
          top: `${fromRect.top}px`,
          left: `${fromRect.left}px`,
          transform: `scale(1, 1)`,
          opacity: 1,
        },
        {
          top: `${toRect.top}px`,
          left: `${toRect.left}px`,
          transform: `scale(${toRect.width / fromRect.width}, ${toRect.height / fromRect.height})`,
          opacity: 0,
        },
      ],
      {
        duration: 20000,
      },
    );
    const tocAnimation = tocLabelTextEl.animate(
      [
        {
          transform: `translate(${fromRect.left - toRect.left}px, ${fromRect.top - toRect.top}px) scale(${fromRect.width / toRect.width}, ${fromRect.height / toRect.height})`,
          opacity: 1,
        },
        {
          transform: `translate(0, 0) scale(1, 1)`,
          opacity: 1,
        },
      ],
      {
        duration: 20000,
      },
    );
    return {
      ghost,
      headingAnimation,
      tocAnimation,
    };
  }
</script>

<div class="container">
  <div class="toc">
    <h2 class="toc-title" bind:this={tocEl}>
      <button class="toc-label" onclick={() => (tocOpen = !tocOpen)}>
        <span class="toc-label-text" bind:this={tocLabelTextEl}>
          {(!tocOpen && currentHeading?.content) || "Table of contents"}
        </span>
        <span class="toc-label-arrow"></span>
      </button>
    </h2>
    {#if tocOpen}
      <ul class="toc-menu">
        {@render tocLinks(toc)}
      </ul>
    {/if}
  </div>
  <div class="content">
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
    <details open>
      <summary>{heading.content}</summary>
      {#if heading.children.length != 0}
        <ul>
          {@render tocLinks(heading.children)}
        </ul>
      {/if}
    </details>
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
  }
  .toc-title {
    display: flex;
    justify-content: space-between;
  }
  .toc-label {
    display: flex;
    gap: 5px;
  }
  .toc-label-text {
    transform-origin: left center;
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
    summary:not(:has(+ ul)) {
      list-style: none;
    }
  }
  .content {
    padding: 0 15px;
    width: 100vw;

    :global {
      .heading-ghost {
        transform-origin: left center;
        z-index: 999;
        margin: 0;
      }
      & :is(h1, h2, h3).current {
        opacity: 0;
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
    font-size: 32px;
  }
  .pointer-label {
    font-size: 16px;
  }
</style>
