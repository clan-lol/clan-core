import type { defineConfig } from "eslint/config";
import type { Linter } from "eslint";
import { fileURLToPath } from "node:url";
import globals from "globals";
import { importX } from "eslint-plugin-import-x";
import { includeIgnoreFile } from "@eslint/compat";
import js from "@eslint/js";
import nodePlugin from "eslint-plugin-n";
import perfectionist from "eslint-plugin-perfectionist";
import prettier from "eslint-config-prettier";
import promisePlugin from "eslint-plugin-promise";
import ts from "typescript-eslint";
import unicorn from "eslint-plugin-unicorn";

function base({
  gitignore,
}: {
  gitignore?: URL | undefined;
}): Parameters<typeof defineConfig>[0] {
  return [
    gitignore ? includeIgnoreFile(fileURLToPath(gitignore)) : [],
    js.configs.all,
    ts.configs.all,
    // @ts-expect-error @typescript-eslint's config is not strict enough to support tsconfig's exactOptionalPropertyTypes
    importX.flatConfigs.recommended,
    // @ts-expect-error @typescript-eslint's config is not strict enough to support tsconfig's exactOptionalPropertyTypes
    importX.flatConfigs.typescript,
    unicorn.configs.recommended,
    prettier,
    {
      files: ["**/*.ts"],
      languageOptions: {
        parserOptions: {
          projectService: true,
        },
      },
    },
    {
      plugins: {
        // Only some of eslint-plugin-promise's rules make sense, so they are
        // turned on individually
        promise: promisePlugin,
        // All perfectionist's rules are for sorting things, so they are
        // turned on individually
        perfectionist,
      },
      /* eslint-disable @typescript-eslint/naming-convention */
      rules: {
        // Typescript-eslint strongly recommend that you do not use the no-undef lint rule on TypeScript projects.
        // See: https://typescript-eslint.io/troubleshooting/faqs/eslint/#i-get-errors-from-the-no-undef-rule-about-global-variables-not-being-defined-even-though-there-are-no-typescript-errors
        "no-undef": "off",
        // Key order sometimes has an conventional order, e.g., "name" comes be "age"
        "sort-keys": "off",
        // Explicitly using == null is conventional to check either null or undefined
        "no-eq-null": "off",
        // File name should provide the meaning
        "no-default-export": "off",
        // Rely on perfectionist/sort-imports instead
        "sort-imports": "off",
        // Identifiers like i, or T in generic types are pretty conventional
        "id-length": "off",
        "max-lines-per-function": "off",
        "max-statements": "off",
        "max-lines": "off",
        "max-classes-per-file": "off",
        // In clash with ts(7030): Not all code paths return a value
        "no-useless-return": "off",
        "no-continue": "off",
        "no-ternary": "off",
        "max-dependencies": "off",
        "no-warning-comments": "off",
        "one-var": ["error", "never"],
        "no-duplicate-imports": ["error", { allowSeparateTypeImports: true }],
        "no-inline-comments": ["error", { ignorePattern: "@vite-ignore" }],
        // Ideally, ["error", { requireFlag: "v" }] should be used, but browser
        // support is not great right now
        "require-unicode-regexp": "off",
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
        // This rule is currently broken, we need T | void as a return type
        // https://github.com/typescript-eslint/typescript-eslint/issues/8755
        "@typescript-eslint/no-invalid-void-type": "off",
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
        "@typescript-eslint/no-use-before-define": [
          "error",
          { functions: false },
        ],
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
        "@typescript-eslint/no-unused-vars": [
          "error",
          {
            varsIgnorePattern: "^_.*",
          },
        ],
        "@typescript-eslint/no-empty-function": [
          "error",
          {
            allow: ["private-constructors", "overrideMethods"],
          },
        ],
        // This creates a lot of false positive. Rely on typescript to catch duplicates instead.
        // https://github.com/un-ts/eslint-plugin-import-x/issues/308
        "import-x/no-duplicates": "off",
        // Typescript already reports such errors
        "import-x/no-unresolved": "off",
        // Typescript already reports such errors
        "import-x/default": "off",
        // Sometimes a package exports a named export that is the same as a
        // property of the default export, which this rules incorrectly warns
        "import-x/no-named-as-default-member": "off",
        "import-x/no-deprecated": "error",
        "import-x/no-extraneous-dependencies": "error",
        "import-x/no-mutable-exports": "error",
        "import-x/no-empty-named-blocks": "error",
        "import-x/newline-after-import": "error",
        // Enforce only way to import default exports
        "import-x/no-named-default": "error",
        "import-x/consistent-type-specifier-style": [
          "error",
          "prefer-top-level",
        ],
        // We require explicit file extensions in import paths to align with
        // Node.js ESM requirements. Since our Vite config and plugins already run
        // as ES Modules, we're maintaining this style across the entire project
        // for Consistency.
        "import-x/extensions": [
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
        "promise/no-multiple-resolved": "error",
        "promise/no-new-statics": "error",
        "promise/no-promise-in-callback": "error",
        "promise/prefer-await-to-callbacks": "error",
        "promise/prefer-await-to-then": "error",
        "promise/param-names": "error",
        "promise/valid-params": "error",
        // Rely on n/prefer-node-protocol instead
        "uncorn/prefer-node-protocol": "off",
        // The same as import/no-empty-named-blocks
        "unicorn/require-module-specifiers": "off",
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
        "unicorn/custom-error-definition": "error",
        "perfectionist/sort-named-exports": "error",
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
    {
      files: ["**/*.d.ts"],
      rules: {
        // Module argument files can use `export {}`
        "import/no-empty-named-blocks": "off",
      },
    },
  ];
}

const node: Linter.Config[] = [
  {
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
  },
  nodePlugin.configs["flat/recommended-module"],
  {
    rules: {
      "require-unicode-regexp": ["error", { requireFlag: "v" }],
      // Rely on typescript to report non-exist imports
      "n/no-missing-import": "off",
      "n/prefer-node-protocol": "error",
      "n/prefer-global/buffer": ["error", "never"],
      "n/prefer-global/process": ["error", "never"],
      "n/prefer-global/console": "error",
      "n/prefer-global/text-decoder": "error",
      "n/prefer-global/text-encoder": "error",
      "n/prefer-global/url": "error",
      "n/prefer-global/url-search-params": "error",
      "unicorn/prefer-import-meta-properties": "error",
    },
  },
];
export const browser: Linter.Config[] = [
  {
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
    rules: {
      // Ideally, ["error", { requireFlag: "v" }] should be used, but browser
      // support is not great right now
      "require-unicode-regexp": "off",
      "import-x/no-nodejs-modules": "error",
    },
  },
];

export default {
  base,
  node,
  browser,
};
