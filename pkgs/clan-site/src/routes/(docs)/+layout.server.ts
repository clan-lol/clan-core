import type { LayoutServerLoad } from "./$types.d.ts";
import type { NavItem } from "$lib/models/docs.ts";
import { getNavItems } from "$lib/models/docs.server.ts";

export const load: LayoutServerLoad<{
  docsNavItems: readonly NavItem[];
}> = async () => ({
  docsNavItems: await getNavItems(),
});
