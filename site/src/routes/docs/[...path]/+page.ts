import { error } from "@sveltejs/kit";
import type { Component } from "svelte";

const articles = import.meta.glob<{
  metadata: {
    layout?: string;
  };
  default: Component;
}>("../**/*.md");

export async function load({ params }) {
  const article = articles[`../${params.path}.md`];
  if (!article) {
    error(404, "");
  }

  const { metadata, default: Content } = await article();
  return {
    Content,
    metadata: {
      ...metadata,
    },
  };
}
