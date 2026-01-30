import type { Article } from "$lib/models/docs.ts";
import type { PageLoad } from "./$types";
import { ArticleNotExistError } from "$lib/models/docs.ts";
import { error } from "@sveltejs/kit";
import { HTTP_NOT_FOUND } from "$lib/util.ts";

export const load: PageLoad<Article> = async ({ params, parent }) => {
  const { docs } = await parent();
  try {
    return await docs.loadArticle(`/${params.path}`);
  } catch (err) {
    if (err instanceof ArticleNotExistError) {
      error(HTTP_NOT_FOUND, String(err));
    } else {
      throw err;
    }
  }
};
