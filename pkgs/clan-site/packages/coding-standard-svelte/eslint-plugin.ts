import type { defineConfig } from "eslint/config";
import type { SvelteConfig } from "@sveltejs/vite-plugin-svelte";
import type { Config as SvelteKitConfig } from "@sveltejs/kit";
import standard from "@clan/coding-standard/eslint";
import svelte from "eslint-plugin-svelte";
import ts from "typescript-eslint";

function base({
  gitignore,
  svelteConfig,
}: {
  gitignore?: URL | undefined;
  svelteConfig: SvelteKitConfig | SvelteConfig;
}): Parameters<typeof defineConfig>[0] {
  // If non-serializable properties are included, running ESLint with the --cache flag will fail.
  // In that case, remove the non-serializable properties
  const sc = ((): SvelteKitConfig | SvelteConfig => {
    if (!("kit" in svelteConfig) || svelteConfig.kit.typescript == null) {
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
    svelte.configs.all,
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
      extends: standard.browser,
      /* eslint-disable @typescript-eslint/naming-convention */
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
        "svelte/block-lang": ["error", { script: ["ts"] }],
        // Deprecated rule
        // https://sveltejs.github.io/eslint-plugin-svelte/rules/no-navigation-without-base/
        "svelte/no-navigation-without-base": "off",
        "svelte/no-unused-class-name": "off",
        "svelte/consistent-selector-style": "off",
      },
    },
  ];
}

const { node, browser } = standard;
export default { base, node, browser };
