import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import tailwind from "eslint-plugin-tailwindcss";

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strict,
  ...tseslint.configs.stylistic,
  ...tailwind.configs["flat/recommended"],
  {
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
    },
  }
);
