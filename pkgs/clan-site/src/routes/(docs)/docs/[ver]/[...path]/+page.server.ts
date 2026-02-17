import type { Article } from "$lib/models/docs.ts";
import type { PageServerLoad } from "./$types.d.ts";
import { ArticleNotExistError, loadArticle } from "$lib/models/docs.server.ts";
import { error } from "@sveltejs/kit";
import { HTTP_NOT_FOUND } from "$lib/util.ts";

export const load: PageServerLoad<{
  docsArticle: Article;
}> = async ({ params, parent }) => {
  const { docsNavItems } = await parent();
  try {
    return {
      docsArticle: await loadArticle(`/${params.path}`, docsNavItems),
    };
  } catch (err) {
    if (err instanceof ArticleNotExistError) {
      error(HTTP_NOT_FOUND, String(err));
    } else {
      throw err;
    }
  }
};
