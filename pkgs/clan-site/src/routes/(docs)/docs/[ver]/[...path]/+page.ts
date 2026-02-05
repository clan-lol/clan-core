import type { PageLoad } from "./$types";
import { ArticleNotExistError, Docs } from "$lib/models/docs.ts";
import { error } from "@sveltejs/kit";
import { HTTP_NOT_FOUND } from "$lib/util.ts";

export const load: PageLoad<{
  docs: Docs;
}> = async ({ params }) => {
  try {
    return {
      docs: await Docs.load(`/${params.path}`),
    };
  } catch (err) {
    if (err instanceof ArticleNotExistError) {
      error(HTTP_NOT_FOUND, String(err));
    } else {
      throw err;
    }
  }
};
