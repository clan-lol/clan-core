import type { ParamMatcher } from "@sveltejs/kit";
import { dev } from "$app/environment";

// SvelteKit doesn't natively support only rendering a page for dev We use a
// param matcher to make the param only match in dev to achieve the same result.
// We do for the test page, which should only exist in dev
export const match = ((param): param is "test" =>
  dev && param === "test") satisfies ParamMatcher;
