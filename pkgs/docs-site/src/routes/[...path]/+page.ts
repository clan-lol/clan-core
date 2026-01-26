import type { Article } from "~/lib/models/docs";
import { error } from "@sveltejs/kit";
import { HttpNotFound } from "$lib/util";
import type { PageLoad } from "./$types";

export const load: PageLoad<Article> = async ({ params, parent }) => {
  const { docs } = await parent();
  const article = await docs.getArticle(`/${params.path}`);
  if (!article) {
    error(HttpNotFound, "");
  }

  return article;
};
