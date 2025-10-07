import { navLinks } from "./settings";
import { normalizeNavLinks } from "./utils";

export async function load() {
  return {
    navLinks: await normalizeNavLinks(navLinks),
  };
}
