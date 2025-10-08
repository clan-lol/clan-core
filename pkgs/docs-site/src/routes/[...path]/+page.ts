import { error } from "@sveltejs/kit";

export async function load({ params, parent }) {
  const { docs } = await parent();
  const article = docs.articles[params.path];
  if (!article) {
    error(404, "");
  }

  const { frontmatter, toc, content } = await article();
  return { frontmatter, toc, content };
}
