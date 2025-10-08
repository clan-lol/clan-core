import { Docs } from "$lib";

export const prerender = true;

export async function load() {
  return {
    docs: await new Docs().init(),
  };
}
