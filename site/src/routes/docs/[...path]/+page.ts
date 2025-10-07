import { error } from "@sveltejs/kit";

const articles = import.meta.glob<{
  content: string;
  frontmatter: {};
  toc: {};
}>("../**/*.md");

export async function load({ params }) {
  const article = articles[`../${params.path.slice(0, -"/".length)}.md`];
  if (!article) {
    error(404, "");
  }

  const { frontmatter, toc, content } = await article();
  return { frontmatter, toc, content };
}
