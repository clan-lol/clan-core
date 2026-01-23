import { error } from "@sveltejs/kit";

export async function load({ params, parent }) {
  const { docs } = await parent();
  const article = await docs.getArticle(`/${params.path}`);
  if (!article) {
    error(404, "");
  }

  return article;
}
