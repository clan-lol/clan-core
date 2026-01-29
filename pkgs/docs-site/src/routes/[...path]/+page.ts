import type { Article } from "~/lib/models/docs";
import { error } from "@sveltejs/kit";
import { HTTP_NOT_FOUND } from "~/lib/util/index.ts";
import type { PageLoad } from "./$types";

export const load: PageLoad<Article> = async ({ params, parent }) => {
  const { docs } = await parent();
  const article = await docs.getArticle(`/${params.path}`);
  if (!article) {
    error(HTTP_NOT_FOUND, "");
  }

  return article;
};
