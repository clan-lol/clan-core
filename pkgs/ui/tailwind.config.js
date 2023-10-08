/** @type {import('tailwindcss').Config} */
import colors from "@clan/colors/colors.json";

const {
  ref: { palette, common },
} = colors;

/**
 * @param {typeof palette} palette
 * @param {string} baseName
 * @returns {import("tailwindcss/types/config").ThemeConfig['colors']}
 */
const getTailwindColors = (palette) => (baseName) =>
  Object.entries(palette).reduce((acc, [_, v]) => {
    if (v.meta.color.baseName === baseName) {
      return {
        ...acc,
        [Math.round(v.meta.color.shade)]: v.value,
      };
    }
    return acc;
  }, {});

module.exports = {
  corePlugins: {
    preflight: false,
  },
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  important: "#__next",
  theme: {
    colors: {
      white: common.white.value,
      black: common.black.value,
      neutral: getTailwindColors(palette)("neutral"),
      purple: {
        ...getTailwindColors(palette)("purple"),
        DEFAULT: palette.purple50.value,
      },
      red: {
        ...getTailwindColors(palette)("red"),
        DEFAULT: palette.red50.value,
      },
      primary: { DEFAULT: palette.green50.value },
      secondary: { DEFAULT: palette.purple50.value },
      paper: {
        dark: palette.neutral5.value,
        light: palette.neutral98.value,
      },
    },
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
