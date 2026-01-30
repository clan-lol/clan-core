import type { LayoutLoad } from "./$types";
import { Docs } from "~/lib/models/docs";

export const load: LayoutLoad<{ docs: Docs }> = async () => ({
  docs: await new Docs().init(),
});
