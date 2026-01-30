import { defineConfig } from "eslint/config";
import globals from "globals";
import importPlugin from "eslint-plugin-import";
import js from "@eslint/js";
import node from "eslint-plugin-n";
import perfectionist from "eslint-plugin-perfectionist";
import prettier from "eslint-config-prettier";
import promisePlugin from "eslint-plugin-promise";
import svelte from "eslint-plugin-svelte";
import svelteConfig from "./svelte.config.ts";
import ts from "typescript-eslint";
import unicorn from "eslint-plugin-unicorn";

export default defineConfig(
  {
    ignores: [".svelte-kit", "build", "static/pagefind"],
  },
  js.configs.all,
  ts.configs.all,
  unicorn.configs.all,
  svelte.configs.all,
  promisePlugin.configs["flat/recommended"],
  prettier,
  svelte.configs.prettier,
  {
    files: ["**/*.ts"],
    languageOptions: {
      parserOptions: {
        projectService: true,
      },
    },
  },
  {
    /* eslint-disable @typescript-eslint/naming-convention */
    rules: {
      // Typescript-eslint strongly recommend that you do not use the no-undef lint rule on TypeScript projects.
      // See: https://typescript-eslint.io/troubleshooting/faqs/eslint/#i-get-errors-from-the-no-undef-rule-about-global-variables-not-being-defined-even-though-there-are-no-typescript-errors
      "no-undef": "off",
      // Key order sometimes has an conventional order, e.g., "name" comes be "age"
      "sort-keys": "off",
      "no-named-export": "off",
      "group-exports": "off",
      "prefer-default-export": "off",
      "no-async-await": "off",
      "no-namespace": "off",
      // Explicitly using == null is conventional to check either null or undefined
      "no-eq-null": "off",
      // File name should provide the meaning
      "no-anonymous-default-export": "off",
      "no-default-export": "off",
      // Rely on perfectionist/sort-imports instead
      "sort-imports": "off",
      // Identifiers like i, or T in generic types are pretty conventional
      "id-length": "off",
      // Having to break up statements like const foo = (bar["key"] ??= "val")
      // is painful. All issues mentioned by the rule's document can eithter be
      // solve by typescript
      "no-multi-assign": "off",
      "no-optional-chaining": "off",
      "max-lines-per-function": "off",
      "max-statements": "off",
      "max-lines": "off",
      "max-classes-per-file": "off",
      "no-rest-spread-properties": "off",
      // In clash with ts(7030): Not all code paths return a value
      "no-useless-return": "off",
      // The same as typescript/no-this-alias
      "no-this-assignment": "off",
      "no-continue": "off",
      "no-ternary": "off",
      "no-unassigned-import": "off",
      "max-dependencies": "off",
      "no-warning-comments": "off",
      // Rely on ts(2454) instead
      "no-unassigned-vars": "off",
      "one-var": ["error", "never"],
      "require-unicode-regexp": ["error", { requireFlag: "v" }],
      eqeqeq: ["error", "always", { null: "ignore" }],
      "no-console": ["error", { allow: ["warn", "error"] }],
      "func-names": ["error", "as-needed"],
      "capitalized-comments": [
        "error",
        "always",
        { ignoreConsecutiveComments: true },
      ],
      "func-style": ["error", "declaration", { allowTypeAnnotation: true }],
      "@typescript-eslint/no-magic-numbers": [
        "error",
        { ignore: [-2, -1, 0, 1, 2] },
      ],
      // It would be very nice to enforce this, but unfortunately this rule
      // doesn't use type information, and can fail in cases where the return
      // can already be inferred. For example
      // function (): Foo { return { method() {} }; }
      "@typescript-eslint/explicit-function-return-type": "off",
      // Clearly show that a promise is being returned
      "@typescript-eslint/return-await": ["error", "always"],
      // Rely on noImplicitReturns from tsconfig as recommanded:
      // https://typescript-eslint.io/rules/consistent-return
      "@typescript-eslint/consistent-return": "off",
      // This is too hard to conform for every function
      "@typescript-eslint/prefer-readonly-parameter-types": "off",
      // It's pretty common to declare a variable and then set it in conditional
      // branches
      "@typescript-eslint/init-declarations": "off",
      // Recommended to be off
      // https://typescript-eslint.io/rules/no-invalid-this/
      "@typescript-eslint/no-invalid-this": "off",
      // Without shadowing, new names are constantly required for potentially
      // the same object
      "@typescript-eslint/no-shadow": "off",
      // Use #private fields for accessibility
      "@typescript-eslint/explicit-member-accessibility": "off",
      // Casting to a narrower type is sometime necessary
      "@typescript-eslint/no-unsafe-type-assertion": "off",
      "@typescript-eslint/no-floating-promises": [
        "error",
        { ignoreIIFE: true },
      ],
      "@typescript-eslint/strict-boolean-expressions": [
        "error",
        {
          allowNullableString: true,
        },
      ],
      "@typescript-eslint/prefer-nullish-coalescing": [
        "error",
        {
          ignorePrimitives: { string: true },
        },
      ],
      "no-duplicate-imports": ["error", { allowSeparateTypeImports: true }],
      "no-inline-comments": ["error", { ignorePattern: "@vite-ignore" }],
      "import/consistent-type-specifier-style": ["error", "prefer-top-level"],
      // We require explicit file extensions in import paths to align with
      // Node.js ESM requirements. Since our Vite config and plugins already run
      // as ES Modules, we’re maintaining this style across the entire project
      // for Consistency.
      "import/extensions": [
        "error",
        "always",
        {
          checkTypeImports: true,
          pathGroupOverrides: [
            { pattern: ".", action: "enforce" },
            { pattern: "..", action: "enforce" },
            { pattern: "./$types", action: "ignore" },
            { pattern: "./*", action: "enforce" },
            { pattern: "../*", action: "enforce" },
            { pattern: "~", action: "enforce" },
            { pattern: "~/*", action: "enforce" },
            { pattern: "$lib", action: "enforce" },
            { pattern: "$lib/**", action: "enforce" },
            { pattern: "**", action: "ignore" },
          ],
        },
      ],
      "unicorn/prefer-export-from": ["error", { ignoreUsedVariables: true }],
      // Sometimes inline functions are need to infer types
      "unicorn/consistent-function-scoping": "off",
      // Even though it would be nice to be able to only use undefined
      // The fact that `undefined` can be overwriten makes it unsafe to use
      "unicorn/no-null": "off",
      // Pretty common to use a, b, i, x, y etc. Impossible to list them all
      "unicorn/prevent-abbreviations": "off",
      "unicorn/explicit-length-check": [
        "error",
        {
          "non-zero": "not-equal",
        },
      ],
      "unicorn/catch-error-name": [
        "error",
        {
          name: "err",
        },
      ],
    },
  },
  {
    files: ["**/*.d.ts"],
    rules: {
      // Module argument files can use `export {}`
      "unicorn/require-module-specifiers": "off",
    },
  },
  {
    files: ["./*.ts", "./packages/vite-plugin-clanmd/**/*.ts"],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
    ...node.configs["flat/all"],
    rules: {
      ...node.configs["flat/all"].rules,
      // Rely on import/extensions instead
      "n/file-extension-in-import": "off",
      // Rely on typescript to report non-exist imports
      "n/no-missing-import": "off",
    },
  },
  {
    files: ["./src/**/*.ts"],
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
    rules: {
      // Ideally, ["error", { requireFlag: "v" }] should be used, but browser
      // support is not great right now
      "require-unicode-regexp": "off",
    },
  },
  {
    files: ["**/*.svelte", "**/*.svelte.ts", "**/*.svelte.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
      },
      parserOptions: {
        parser: ts.parser,
        projectService: true,
        extraFileExtensions: [".svelte"],
        svelteConfig,
      },
    },
    rules: {
      // Types are not inferred correctly by typescript-eslint for page/layout
      // data props for example
      "@typescript-eslint/no-unsafe-assignment": "off",
      // Type are not inferred correctly by typescript-eslint for page/layout
      // data props for example
      "@typescript-eslint/no-unsafe-member-access": "off",
      // Type are not inferred correctly by typescript-eslint for page/layout
      // data props for example
      "@typescript-eslint/no-unsafe-call": "off",
      // Type are not inferred correctly by typescript-eslint for page/layout
      // data props for example
      "@typescript-eslint/no-unsafe-argument": "off",
      // Template like {@render navItems(item.items)} report such an error,
      // where it shouldn't
      "@typescript-eslint/no-confusing-void-expression": "off",
      // Calling Svelte snippets can report such an error where it shouldn't
      "@typescript-eslint/no-use-before-define": "off",
      "svelte/block-lang": ["error", { script: ["ts"] }],
      // Deprecated rule
      // https://sveltejs.github.io/eslint-plugin-svelte/rules/no-navigation-without-base/
      "svelte/no-navigation-without-base": "off",
      "svelte/no-unused-class-name": "off",
      "svelte/consistent-selector-style": "off",
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
      "perfectionist/sort-named-imports": "error",
      "perfectionist/sort-imports": [
        "error",
        {
          sortBy: "specifier",
          newlinesBetween: 0,
          tsconfig: { rootDir: "." },
          groups: ["type", "value-import", "side-effect", "unknown"],
        },
      ],
    },
  },
);
