import eslint from "@eslint/js";
import prettier from "eslint-config-prettier/flat";
import tseslint from "typescript-eslint";
import globals from "globals";
import svelte from "eslint-plugin-svelte";
import { defineConfig } from "eslint/config";
import svelteConfig from "./svelte.config.ts";

export default defineConfig(
  {
    ignores: [".svelte-kit/**/*", "build/**/*", "static/pagefind/**/*"],
  },
  eslint.configs.all,
  prettier,
  tseslint.configs.strict,
  tseslint.configs.stylistic,
  svelte.configs.recommended,
  svelte.configs.prettier,
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
  },
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      // Typescript-eslint strongly recommend that you do not use the no-undef lint rule on TypeScript projects.
      // See: https://typescript-eslint.io/troubleshooting/faqs/eslint/#i-get-errors-from-the-no-undef-rule-about-global-variables-not-being-defined-even-though-there-are-no-typescript-errors
      "no-undef": "off",
      "sort-imports": "off",
      "sort-keys": "off",
      "sort-vars": "off",
      "id-length": "off",
      "one-var": "off",
      "no-shadow": "off",
      "max-lines-per-function": "off",
      "max-statements": "off",
      "max-lines": "off",
      "require-unicode-regexp": "off",
      // We use exactOptionalPropertyTypes in tsconfig.json, which might require dot notation
      "dot-notation": "off",
      "init-declarations": "off",
      // This is a duplicate of @typescript-eslint/no-this-alias, which is more configurable
      "consistent-this": "off",
      "no-ternary": "off",
      "no-continue": "off",
      // Rely on typescript to catch return type error
      "consistent-return": "off",
      // In clash with ts(7030): Not all code paths return a value
      "no-useless-return": "off",
      "no-warning-comments": "off",
      "no-use-before-define": ["error", { functions: false }],
      "no-console": ["error", { allow: ["warn", "error"] }],
      "no-magic-numbers": ["error", { ignore: [-2, -1, 0, 1, 2] }],
      "func-style": ["error", "declaration", { allowTypeAnnotation: true }],
      "capitalized-comments": [
        "off",
        "always",
        { ignoreConsecutiveComments: true },
      ],
      "@typescript-eslint/no-invalid-void-type": [
        "error",
        { allowAsThisParameter: true },
      ],
    },
  },
);
