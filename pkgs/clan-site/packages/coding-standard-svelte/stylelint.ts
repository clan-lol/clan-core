import type { Config } from "stylelint";

export * from "@clan.lol/coding-standard/stylelint";

export default {
  extends: ["@clan.lol/coding-standard/stylelint"],
  ignoreFiles: [".svelte-kit/**"],
  overrides: [
    {
      files: ["**/*.svelte"],
      customSyntax: "postcss-html",
      rules: {
        "selector-pseudo-class-no-unknown": [
          true,
          { ignorePseudoClasses: ["global"] },
        ],
      },
    },
  ],
} satisfies Config;
