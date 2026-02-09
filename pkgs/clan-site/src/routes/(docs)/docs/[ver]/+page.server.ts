import type { Article } from "$lib/models/docs.ts";
import type { PageServerLoad } from "./$types.d.ts";
import { loadArticle } from "$lib/models/docs.ts";

export const load: PageServerLoad<{
  docsArticle: Article;
}> = async ({ parent }) => {
  const { docsNavItems } = await parent();
  const docsArticle = await loadArticle("/", docsNavItems);
  return { docsArticle };
};
