import { navLinks } from "./settings";
import { normalizeNavLinks } from "./utils";

export function load() {
  return {
    navLinks: normalizeNavLinks(navLinks),
  };
}
