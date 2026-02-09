// TODO: change this file to .ts once stylelint stops failing randomly
// https://github.com/stylelint/stylelint/issues/8893
export default {
  extends: ["@clan/coding-standard-svelte/stylelint"],
  ignoreFiles: ["build/**", "static/_pagefind/**", "src/docs/**"],
};
