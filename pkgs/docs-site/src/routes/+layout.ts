import { Docs } from "$lib/models/docs/index.ts";
import type { LayoutLoad } from "./$types";

export const prerender = true;

export const load: LayoutLoad<{ docs: Docs }> = async () => ({
  docs: await new Docs().init(),
});
