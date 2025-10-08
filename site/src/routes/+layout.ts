import * as config from "~/config";
import { Docs } from "./docs";

export const prerender = true;
export const trailingSlash = "always";

export async function load({ url }) {
  const path = url.pathname.endsWith("/")
    ? url.pathname.slice(0, -1)
    : url.pathname;
  return {
    docs:
      path != config.docs.base && !path.startsWith(`${config.docs.base}/`)
        ? null
        : await new Docs().init(),
  };
}
