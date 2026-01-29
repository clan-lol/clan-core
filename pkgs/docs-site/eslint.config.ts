// The actual linting is handled by oxlint (see .oxlintrc.json)
// We use eslint as a formatter to do things like sort imports which prettier
// doesn't do. Your editor should be configured to run
//
// eslint --flag unstable_native_nodejs_ts_config --no-inline-config
// prettier -w .
//
// In that order, when saving a file
import { defineConfig } from "eslint/config";
import importPlugin from "eslint-plugin-import";
import perfectionist from "eslint-plugin-perfectionist";
import svelte from "eslint-plugin-svelte";
import svelteConfig from "./svelte.config.ts";
import ts from "typescript-eslint";

export default defineConfig(
  {
    ignores: [".svelte-kit/**/*", "build/**/*", "static/pagefind/**/*"],
  },
  ts.configs.base,
  svelte.configs.base,
  {
    files: ["**/*.js", "**/*.ts"],
  },
  {
    files: ["**/*.svelte", "**/*.svelte.ts", "**/*.svelte.js"],
    languageOptions: {
      parserOptions: {
        parser: ts.parser,
        projectService: true,
        extraFileExtensions: [".svelte"],
        svelteConfig,
      },
    },
    rules: {
      "svelte/no-raw-special-elements": "error",
      "svelte/no-useless-mustaches": "error",
      "svelte/prefer-const": "error",
    },
  },
  {
    plugins: {
      import: importPlugin,
      perfectionist,
    },
    rules: {
      "import/enforce-node-protocol-usage": ["error", "always"],
      "import/no-relative-packages": "error",
      "import/consistent-type-specifier-style": ["error", "prefer-top-level"],
      "import/newline-after-import": "error",
      "import/no-useless-path-segments": "error",
      "import/no-absolute-path": "error",
      "import/no-duplicates": "error",
      "perfectionist/sort-array-includes": "error",
      "perfectionist/sort-imports": [
        "error",
        {
          sortBy: "specifier",
          newlinesBetween: 0,
          tsconfig: { rootDir: "." },
          groups: [
            "side-effect",
            "wildcard-import",
            "multiline-import",
            "singleline-import",
          ],
        },
      ],
    },
  },
);
