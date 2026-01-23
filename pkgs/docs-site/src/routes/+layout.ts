import { Docs } from "$lib/models/docs";

export const prerender = true;

export async function load() {
  return {
    docs: await new Docs().init(),
  };
}
