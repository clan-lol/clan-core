import { error } from "@sveltejs/kit";
import type { Component } from "svelte";

const articles = import.meta.glob<{
  default: string;
  frontmatter: {};
  toc: {};
}>("../**/*.md");

export async function load({ params }) {
  const article = articles[`../${params.path.slice(0, -"/".length)}.md`];
  if (!article) {
    error(404, "");
  }

  const { frontmatter, toc, default: content } = await article();
  return {
    content,
    frontmatter,
    toc,
  };
}
