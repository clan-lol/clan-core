import { Docs } from "$lib/models/docs";
import type { LayoutLoad } from "./$types";

export const prerender = true;

export const load: LayoutLoad<{ docs: Docs }> = async () => {
  return {
    docs: await new Docs().init(),
  };
};
