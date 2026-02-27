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

export function base({
  gitignore,
}: {
  gitignore?: URL | undefined;
}): Parameters<typeof defineConfig>[0] {
  return [
    gitignore ? includeIgnoreFile(fileURLToPath(gitignore)) : [],
    { ignores: ["**/*.js"] },
    js.configs.recommended,
    ts.configs.strictTypeChecked,
    ts.configs.stylisticTypeChecked,
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
      rules: {
        "array-callback-return": ["error", { checkForEach: true }],
        // Err on the side of caution. Use ESLint disable comment when needed
        "no-await-in-loop": "error",
        "no-duplicate-imports": ["error", { allowSeparateTypeImports: true }],
        "no-fallthrough": ["error", { reportUnusedFallthroughComment: true }],
        "no-inline-comments": ["error", { ignorePattern: "@vite-ignore" }],
        "no-promise-executor-return": "error",
        // Err on the side of causion.  Use ESLint disable comment when needed
        "no-template-curly-in-string": "error",
        // Err on the side of causion.  Use ESLint disable comment when needed
        "no-unmodified-loop-condition": "error",
        // Err on the side of causion.  Use ESLint disable comment when needed
        "no-unreachable-loop": "error",
        "no-unsafe-negation": ["error", { enforceForOrderingRelations: true }],
        "no-unsafe-optional-chaining": [
          "error",
          { disallowArithmeticOperators: true },
        ],
        "valid-typeof": ["error", { requireStringLiterals: true }],
        "accessor-pairs": ["error", { enforceForTSTypes: true }],
        "arrow-body-style": ["error", "as-needed"],
        "capitalized-comments": [
          "error",
          "always",
          { ignoreConsecutiveComments: true },
        ],
        curly: "error",
        // Rely on @typescript-eslint/switch-exhaustiveness-check instead
        "default-case": "off",
        "default-case-last": "error",
        eqeqeq: ["error", "always", { null: "ignore" }],
        "func-name-matching": ["error", { considerPropertyDescriptor: true }],
        "func-names": ["error", "as-needed"],
        "func-style": ["error", "declaration", { allowTypeAnnotation: true }],
        "grouped-accessor-pairs": [
          "error",
          "getBeforeSet",
          { enforceForTSTypes: true },
        ],
        "guard-for-in": "error",
        "logical-assignment-operators": [
          "error",
          "always",
          { enforceForIfStatements: true },
        ],
        "max-depth": "error",
        "new-cap": ["error", { properties: true }],
        "no-alert": "error",
        "no-console": ["error", { allow: ["warn", "error"] }],
        "no-else-return": "error",
        "no-eval": "error",
        "no-extend-native": "error",
        "no-extra-bind": "error",
        "no-extra-boolean-cast": [
          "error",
          { enforceForInnerExpressions: true },
        ],
        "no-extra-label": "error",
        "no-implicit-coercion": "error",
        "no-iterator": "error",
        "no-lone-blocks": "error",
        "no-lonely-if": "error",
        "no-negated-condition": "error",
        "no-nested-ternary": "error",
        "no-new": "error",
        "no-new-func": "error",
        "no-new-wrappers": "error",
        "no-object-constructor": "error",
        "no-octal-escape": "error",
        "no-param-reassign": "error",
        "no-plusplus": "error",
        "no-proto": "error",
        "no-return-assign": "error",
        "no-script-url": "error",
        "no-sequences": "error",
        "no-undef-init": "error",
        "no-underscore-dangle": "error",
        "no-unneeded-ternary": "error",
        "no-useless-call": "error",
        "no-useless-computed-key": "error",
        "no-useless-constructor": "error",
        "no-useless-rename": "error",
        "no-void": "error",
        "no-warning-comments": "warn",
        "object-shorthand": "error",
        "one-var": ["error", "never"],
        "operator-assignment": "error",
        "prefer-arrow-callback": ["error", { allowNamedFunctions: false }],
        "prefer-exponentiation-operator": "error",
        "prefer-named-capture-group": "error",
        "prefer-numeric-literals": "error",
        "prefer-object-has-own": "error",
        "prefer-object-spread": "error",
        "prefer-promise-reject-errors": "error",
        "prefer-regex-literals": "error",
        "prefer-template": "error",
        "preserve-caught-error": ["error", { requireCatchParameter: true }],
        radix: "error",
        // Ideally, ["error", { requireFlag: "v" }] should be used, but browser
        // support is not great right now
        "require-unicode-regexp": "off",
        "symbol-description": "error",
        yoda: "error",
        "unicode-bom": "error",
        "@typescript-eslint/consistent-type-exports": "error",
        "@typescript-eslint/consistent-type-imports": "error",
        "@typescript-eslint/class-methods-use-this": [
          "error",
          { ignoreOverrideMethods: true },
        ],
        "@typescript-eslint/default-param-last": "error",
        "@typescript-eslint/explicit-module-boundary-types": "error",
        // It would be very nice to enforce this, but unfortunately this rule
        // doesn't use type information, and can fail in cases where the return
        // can already be inferred. For example
        // function (): Foo { return { method() {} }; }
        "@typescript-eslint/explicit-function-return-type": "off",
        "@typescript-eslint/explicit-member-accessibility": "error",
        // TODO: figure this rule out, currently it's too complex to spend time on,
        // but we do want an order like static, public, protected, private
        "@typescript-eslint/method-signature-style": "error",
        "@typescript-eslint/member-ordering": "off",
        "@typescript-eslint/no-empty-function": [
          "error",
          {
            allow: ["private-constructors", "overrideMethods"],
          },
        ],
        "@typescript-eslint/no-explicit-any": ["error", { fixToUnknown: true }],
        "@typescript-eslint/no-import-type-side-effects": "error",
        // This rule is currently broken, we need T | void as a return type
        // https://github.com/typescript-eslint/typescript-eslint/issues/8755
        "@typescript-eslint/no-invalid-void-type": "off",
        "@typescript-eslint/no-magic-numbers": [
          "error",
          { ignore: [-2, -1, 0, 1, 2] },
        ],
        // Casting to a narrower type is sometime necessary
        "@typescript-eslint/no-unsafe-type-assertion": "off",
        "@typescript-eslint/no-unused-vars": [
          "error",
          {
            ignoreUsingDeclarations: true,
            varsIgnorePattern: "^_.*",
          },
        ],
        // Putting utility functions at the button and rely on hoisting is a
        // common pattern
        // Two classes might call each other to create a tree structure
        "@typescript-eslint/no-use-before-define": [
          "error",
          { functions: false, classes: false },
        ],
        "@typescript-eslint/no-useless-empty-export": "error",
        "@typescript-eslint/parameter-properties": "error",
        "@typescript-eslint/prefer-destructuring": "error",
        // This is too hard to conform for every function
        "@typescript-eslint/prefer-readonly-parameter-types": "off",
        "@typescript-eslint/promise-function-async": "error",
        "@typescript-eslint/prefer-nullish-coalescing": [
          "error",
          {
            ignorePrimitives: { string: true },
          },
        ],
        "@typescript-eslint/require-array-sort-compare": "error",
        // Clearly show that a promise is being returned
        "@typescript-eslint/return-await": ["error", "always"],
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
        "@typescript-eslint/strict-void-return": "error",
        "@typescript-eslint/switch-exhaustiveness-check": [
          "error",
          {
            allowDefaultCaseForExhaustiveSwitch: false,
            requireDefaultForNonUnion: true,
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
        // Ambient declarations might use import()
        "@typescript-eslint/consistent-type-imports": "off",
        // Module argument files can use `export {}`
        "import/no-empty-named-blocks": "off",
      },
    },
  ];
}

export const node: Linter.Config[] = [
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
      // Rely on typescript to report non-exist imports
      "n/no-missing-import": "off",
      "n/prefer-node-protocol": "error",
      "n/prefer-global/buffer": "error",
      "n/prefer-global/process": "error",
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
      "import-x/no-nodejs-modules": "error",
    },
  },
];

export const universal: Linter.Config[] = [
  {
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.browser,
      },
    },
  },
  {
    rules: {
      "import-x/no-nodejs-modules": "error",
    },
  },
];
