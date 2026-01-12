/**
 * @see https://prettier.io/docs/en/configuration.html
 * @type {import("prettier").Config}
 */
const config = {
  trailingComma: "all",
  // FIXME: enable this after figuring out how to package prettier-plugin-tailwindcss
  // needed by treefmt
  // plugins: ["prettier-plugin-tailwindcss"],
};

export default config;
