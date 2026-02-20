// TODO: change this file to .ts once stylelint stops failing randomly
// https://github.com/stylelint/stylelint/issues/8893
import * as standard from "@clan/coding-standard/stylelint";

export default {
  extends: ["@clan/coding-standard-svelte/stylelint"],
  ignoreFiles: ["build/**", "static/_pagefind/**", "src/docs/**"],
  rules: {
    ...standard.base({
      customProperties: new URL(
        "src/css/custom-properties.css",
        import.meta.url,
      ),
      customMedia: new URL("src/css/custom-media.css", import.meta.url),
    }),
  },
};
