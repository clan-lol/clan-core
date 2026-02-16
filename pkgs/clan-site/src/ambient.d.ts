/// <reference types="@poppanator/sveltekit-svg/dist/svg.d.ts" />

// This is needed to address eslint type limitation
// https://sveltejs.github.io/eslint-plugin-svelte/user-guide/#you-re-using-type-script-and-the-imported-svelte-component-types-cannot-be-resolved-or-appear-to-be
//
// We can't use typescript-eslint-parser-for-extra-files as suggested by the FAQ because it doesn't support eslint 9
// https://github.com/ota-meshi/typescript-eslint-parser-for-extra-files/issues/162
//
// Instead we simply manually provide tht types
declare module "~/routes/(docs)/docs/[ver]/+page.svelte" {
  export const title: string;
}
