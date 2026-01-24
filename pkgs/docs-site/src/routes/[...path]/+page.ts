import { error } from "@sveltejs/kit";
import { HttpNotFound } from "$lib/util";

export async function load({ params, parent }) {
  const { docs } = await parent();
  const article = await docs.getArticle(`/${params.path}`);
  if (!article) {
    error(HttpNotFound, "");
  }

  return article;
}
