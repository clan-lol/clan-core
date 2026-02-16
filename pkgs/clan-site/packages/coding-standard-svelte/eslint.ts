import type { defineConfig } from "eslint/config";
import type { SvelteConfig } from "@sveltejs/vite-plugin-svelte";
import type { Config as SvelteKitConfig } from "@sveltejs/kit";
import * as standard from "@clan/coding-standard/eslint";
import svelte from "eslint-plugin-svelte";
import ts from "typescript-eslint";

export function base({
  gitignore,
  svelteConfig,
}: {
  gitignore?: URL | undefined;
  svelteConfig: SvelteKitConfig | SvelteConfig;
}): Parameters<typeof defineConfig>[0] {
  // If non-serializable properties are included, running ESLint with the --cache flag will fail.
  // In that case, remove the non-serializable properties
  const sc = ((): SvelteKitConfig | SvelteConfig => {
    if (!("kit" in svelteConfig) || !svelteConfig.kit.typescript) {
      return svelteConfig;
    }
    const { typescript: _, ...kit } = svelteConfig.kit;
    return {
      ...svelteConfig,
      kit,
    };
  })();
  return [
    standard.base({ gitignore }),
    svelte.configs["flat/recommended"],
    svelte.configs.prettier,
    {
      files: [
        "./*.ts",
        "./src/**/*.server.ts",
        "./src/**/+server.ts",
        "./src/**/*.server/**/*.ts",
      ],
      extends: standard.node,
    },
    {
      files: ["**/*.svelte", "**/*.svelte.ts"],
      languageOptions: {
        parserOptions: {
          parser: ts.parser,
          projectService: true,
          extraFileExtensions: [".svelte"],
          svelteConfig: sc,
        },
      },
      extends: standard.universal,
      rules: {
        // Due to limitation of eslint-plugin-svelte, these rules create unavoidable false positives
        // https://sveltejs.github.io/eslint-plugin-svelte/user-guide/#settings-svelte
        "@typescript-eslint/no-unsafe-assignment": "off",
        "@typescript-eslint/no-unsafe-member-access": "off",
        "@typescript-eslint/no-unsafe-call": "off",
        "@typescript-eslint/no-unsafe-return": "off",
        "@typescript-eslint/no-unsafe-argument": "off",

        // Template like {@render navItems(item.items)} report such an error,
        // where it shouldn't
        "@typescript-eslint/no-confusing-void-expression": "off",
        "svelte/block-lang": ["error", { script: ["ts"] }],
        "svelte/no-add-event-listener": "error",
        "svelte/no-target-blank": "error",
        "svelte/no-inline-styles": "error",
        "svelte/no-unused-class-name": "error",
        "svelte/prefer-class-directive": "error",
        "svelte/prefer-style-directive": "error",
        "svelte/require-event-prefix": "error",
        "svelte/spaced-html-comment": "error",
      },
    },
  ];
}

const { browser, node, universal } = standard;
export { browser, node, universal };
