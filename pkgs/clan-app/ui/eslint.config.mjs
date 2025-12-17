// For more info, see https://github.com/storybookjs/eslint-plugin-storybook#configuration-flat-config-format
import storybook from "eslint-plugin-storybook";

import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import tailwind from "eslint-plugin-tailwindcss";
import { globalIgnores } from "eslint/config";
import unusedImports from "eslint-plugin-unused-imports";

const config = tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strict,
  ...tseslint.configs.stylistic,
  ...tailwind.configs["flat/recommended"],
  globalIgnores(["src/types/index.d.ts"]),
  {
    plugins: {
      "unused-imports": unusedImports,
    },
    rules: {
      "tailwindcss/no-contradicting-classname": [
        "error",
        {
          callees: ["cx"],
        },
      ],
      "tailwindcss/no-custom-classname": [
        "error",
        {
          callees: ["cx"],
          whitelist: ["material-icons"],
        },
      ],
      // Fixme: needed by deleteMachine, find a way to re-enable this
      "@typescript-eslint/no-dynamic-delete": "off",
      // modular-forms explicitly requires `type` instead of `interface`
      // https://github.com/fabian-hiller/modular-forms/issues/2
      "@typescript-eslint/consistent-type-definitions": "off",
      // TODO: make this more strict by removing later
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "unused-imports/no-unused-imports": "warn",
      "@typescript-eslint/no-non-null-assertion": "off",
    },
  },
);

export default config;
