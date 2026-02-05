import type { PageLoad } from "./$types";
import { Docs } from "$lib/models/docs.ts";

export const load: PageLoad<{
  docs: Docs;
}> = async () => ({
  docs: await Docs.load("/"),
});
