import { error } from "@sveltejs/kit";
import type { Component } from "svelte";

const articles = import.meta.glob<{
  default: string;
}>("../**/*.md");

export async function load({ params }) {
  const article = articles[`../${params.path.slice(0, -"/".length)}.md`];
  if (!article) {
    error(404, "");
  }

  const content = await article();
  return {
    content: content.default,
  };
}
