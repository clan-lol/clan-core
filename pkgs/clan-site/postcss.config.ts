import type { Config } from "postcss-load-config";
import postcssGlobalData from "@csstools/postcss-global-data";
import postcssPresetEnv from "postcss-preset-env";

const config: Config = {
  plugins: [
    postcssGlobalData({
      files: ["./src/css/custom-media.css", "./src/css/custom-properties.css"],
    }),
    postcssPresetEnv(),
  ],
};
export default config;
