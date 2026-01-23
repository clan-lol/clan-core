// TODO: use this once storybook is fixed
// import storybook from "eslint-plugin-storybook";

import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import globals from "globals";
import svelte from "eslint-plugin-svelte";
import { defineConfig } from "eslint/config";
import svelteConfig from "./svelte.config.ts";

export default defineConfig(
  {
    ignores: [".svelte-kit/**/*", "build/**/*", "static/pagefind/**/*"],
  },
  eslint.configs.recommended,
  tseslint.configs.strict,
  tseslint.configs.stylistic,
  svelte.configs.recommended,
  svelte.configs.prettier,
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      // typescript-eslint strongly recommend that you do not use the no-undef lint rule on TypeScript projects.
      // see: https://typescript-eslint.io/troubleshooting/faqs/eslint/#i-get-errors-from-the-no-undef-rule-about-global-variables-not-being-defined-even-though-there-are-no-typescript-errors
      "no-undef": "off",
    },
  },
  {
    files: ["**/*.svelte", "**/*.svelte.ts", "**/*.svelte.js"],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
        projectService: true,
        extraFileExtensions: [".svelte"],
        svelteConfig,
      },
    },
    rules: {
      "@typescript-eslint/no-invalid-void-type": [
        "error",
        { allowAsThisParameter: true },
      ],
      "@typescript-eslint/restrict-template-expressions": [
        "error",
        {
          allowNumber: true,
        },
      ],
      "@typescript-eslint/prefer-nullish-coalescing": [
        "error",
        { ignorePrimitives: { string: true } },
      ],
    },
  },
);
