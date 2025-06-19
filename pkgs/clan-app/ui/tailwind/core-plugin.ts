import plugin from "tailwindcss/plugin";
// @ts-expect-error: lib of tailwind has no types
import { parseColor } from "tailwindcss/lib/util/color";

/* Converts HEX color to RGB */
const toRGB = (value: string) =>
  "rgb(" + parseColor(value).color.join(" ") + ")";

const mkBorderUtils = (
  theme: (n: string) => unknown,
  prefix: string,
  cssProperty: string,
) => ({
  // - def colors
  [`.${prefix}-def-1`]: {
    [cssProperty]: theme("colors.secondary.100"),
  },
  [`.${prefix}-def-2`]: {
    [cssProperty]: theme("colors.secondary.200"),
  },
  [`.${prefix}-def-3`]: {
    [cssProperty]: theme("colors.secondary.300"),
  },
  [`.${prefix}-def-4`]: {
    [cssProperty]: theme("colors.secondary.400"),
  },
  // - def acc colors
  [`.${prefix}-def-acc-1`]: {
    [cssProperty]: theme("colors.secondary.500"),
  },
  [`.${prefix}-def-acc-2`]: {
    [cssProperty]: theme("colors.secondary.900"),
  },
  [`.${prefix}-def-acc-3`]: {
    [cssProperty]: theme("colors.secondary.900"),
  },
  [`.${prefix}-def-acc-4`]: {
    [cssProperty]: theme("colors.secondary.950"),
  },
  // - inverse colors
  [`.${prefix}-inv-1`]: {
    [cssProperty]: theme("colors.secondary.700"),
  },
  [`.${prefix}-inv-2`]: {
    [cssProperty]: theme("colors.secondary.800"),
  },
  [`.${prefix}-inv-3`]: {
    [cssProperty]: theme("colors.secondary.900"),
  },
  [`.${prefix}-inv-4`]: {
    [cssProperty]: theme("colors.secondary.950"),
  },
  // - inverse acc
  [`.${prefix}-inv-acc-1`]: {
    [cssProperty]: theme("colors.secondary.300"),
  },
  [`.${prefix}-inv-acc-2`]: {
    [cssProperty]: theme("colors.secondary.200"),
  },
  [`.${prefix}-inv-acc-3`]: {
    [cssProperty]: theme("colors.secondary.100"),
  },
  [`.${prefix}-inv-acc-4`]: {
    [cssProperty]: theme("colors.secondary.50"),
  },
  [`.${prefix}-int-1`]: {
    [cssProperty]: theme("colors.info.500"),
  },
  [`.${prefix}-int-2`]: {
    [cssProperty]: theme("colors.info.600"),
  },
  [`.${prefix}-int-3`]: {
    [cssProperty]: theme("colors.info.700"),
  },
  [`.${prefix}-int-4`]: {
    [cssProperty]: theme("colors.info.800"),
  },

  [`.${prefix}-semantic-1`]: {
    [cssProperty]: theme("colors.error.500"),
  },
  [`.${prefix}-semantic-2`]: {
    [cssProperty]: theme("colors.error.600"),
  },
  [`.${prefix}-semantic-3`]: {
    [cssProperty]: theme("colors.error.700"),
  },
  [`.${prefix}-semantic-4`]: {
    [cssProperty]: theme("colors.error.800"),
  },
});

export default plugin.withOptions(
  (_options = {}) =>
    ({ addUtilities, theme, addVariant, e }) => {
      // @ts-expect-error: lib of tailwind has no types
      addVariant("popover-open", ({ modifySelectors, separator }) => {
        // @ts-expect-error: lib of tailwind has no types
        modifySelectors(({ className }) => {
          return `.${e(`popover-open${separator}${className}`)}:popover-open`;
        });
      });
      addUtilities({
        // Background colors

        // default
        ".bg-def-1": {
          backgroundColor: theme("colors.white"),
        },
        ".bg-def-2": {
          backgroundColor: theme("colors.secondary.50"),
        },
        ".bg-def-3": {
          backgroundColor: theme("colors.secondary.100"),
        },
        ".bg-def-4": {
          backgroundColor: theme("colors.secondary.200"),
        },
        // default accessible
        ".bg-def-acc-1": {
          backgroundColor: theme("colors.primary.50"),
        },
        ".bg-def-acc-2": {
          backgroundColor: theme("colors.secondary.100"),
        },
        ".bg-def-acc-3": {
          backgroundColor: theme("colors.secondary.200"),
        },
        ".bg-def-acc-4": {
          backgroundColor: theme("colors.secondary.300"),
        },
        // bg inverse
        ".bg-inv-1": {
          backgroundColor: theme("colors.primary.600"),
        },
        ".bg-inv-2": {
          backgroundColor: theme("colors.primary.700"),
        },
        ".bg-inv-3": {
          backgroundColor: theme("colors.primary.800"),
        },
        ".bg-inv-4": {
          backgroundColor: theme("colors.primary.900"),
        },
        // bg inverse accessible
        ".bg-inv-acc-1": {
          backgroundColor: theme("colors.secondary.500"),
        },
        ".bg-inv-acc-2": {
          backgroundColor: theme("colors.secondary.600"),
        },
        ".bg-inv-acc-3": {
          backgroundColor: theme("colors.secondary.700"),
        },
        ".bg-inv-acc-4": {
          backgroundColor: theme("colors.primary.950"),
        },

        // bg inverse accent
        ".bg-semantic-1": {
          backgroundColor: theme("colors.error.50"),
        },
        ".bg-semantic-2": {
          backgroundColor: theme("colors.error.100"),
        },
        ".bg-semantic-3": {
          backgroundColor: theme("colors.error.200"),
        },
        ".bg-semantic-4": {
          backgroundColor: theme("colors.error.300"),
        },

        // Text colors
        ".fg-def-1": {
          color: theme("colors.secondary.950"),
        },
        ".fg-def-2": {
          color: theme("colors.secondary.900"),
        },
        ".fg-def-3": {
          color: theme("colors.secondary.700"),
        },
        ".fg-def-4": {
          color: theme("colors.secondary.400"),
        },
        // fg inverse
        ".fg-inv-1": {
          color: theme("colors.white"),
        },
        ".fg-inv-2": {
          color: theme("colors.secondary.100"),
        },
        ".fg-inv-3": {
          color: theme("colors.secondary.300"),
        },
        ".fg-inv-4": {
          color: theme("colors.secondary.400"),
        },

        ".fg-semantic-1": {
          color: theme("colors.error.500"),
        },
        ".fg-semantic-2": {
          color: theme("colors.error.600"),
        },
        ".fg-semantic-3": {
          color: theme("colors.error.700"),
        },
        ".fg-semantic-4": {
          color: theme("colors.error.800"),
        },

        ...mkBorderUtils(theme, "border", "borderColor"),
        ...mkBorderUtils(theme, "border-b", "borderBottom"),
        ...mkBorderUtils(theme, "border-t", "borderTop"),
        ...mkBorderUtils(theme, "border-l", "borderLeft"),
        ...mkBorderUtils(theme, "border-r", "borderRight"),

        // Example: dark mode utilities (all elements within <html class="dark"> )
        // ".dark .bg-def-1": {
        //   backgroundColor: theme("colors.black"),
        // },
        // ".dark .bg-def-2": {
        //   backgroundColor: theme("colors.primary.900"),
        // },
        // ".dark .bg-def-3": {
        //   backgroundColor: theme("colors.primary.800"),
        // },
        // ".dark .bg-def-4": {
        //   backgroundColor: theme("colors.primary.700"),
        // },
        // ".dark .bg-def-5": {
        //   backgroundColor: theme("colors.primary.600"),
        // },
      });
      // add more base styles
    },
  // add configuration which is merged with the final config
  () => ({
    theme: {
      extend: {
        colors: {
          white: toRGB("#ffffff"),
          black: toRGB("#000000"),
          primary: {
            50: toRGB("#f4f9f9"),
            100: toRGB("#dbeceb"),
            200: toRGB("#b6d9d6"),
            300: toRGB("#8abebc"),
            400: toRGB("#478585"),
            500: toRGB("#526f6f"),
            600: toRGB("#4b6767"),
            700: toRGB("#345253"),
            800: toRGB("#2e4a4b"),
            900: toRGB("#203637"),
            950: toRGB("#162324"),
          },
          secondary: {
            50: toRGB("#f7f9fA"),
            100: toRGB("#e7f2f4"),
            200: toRGB("#d8e8eb"),
            300: toRGB("#afc6ca"),
            400: toRGB("#90b2b7"),
            500: toRGB("#7b9b9f"),
            600: toRGB("#4f747A"),
            700: toRGB("#415e63"),
            800: toRGB("#446065"),
            900: toRGB("#2c4347"),
            950: toRGB("#0d1416"),
          },
          info: {
            50: toRGB("#eff9ff"),
            100: toRGB("#dff2ff"),
            200: toRGB("#b8e8ff"),
            300: toRGB("#78d6ff"),
            400: toRGB("#2cc0ff"),
            500: toRGB("#06aaf1"),
            600: toRGB("#006ca7"),
            700: toRGB("#006ca7"),
            800: toRGB("#025b8a"),
            900: toRGB("#084c72"),
            950: toRGB("#06304b"),
          },
          error: {
            50: toRGB("#fcf3f8"),
            100: toRGB("#f9eaf4"),
            200: toRGB("#f5d5e9"),
            300: toRGB("#ea9ecb"),
            400: toRGB("#e383ba"),
            500: toRGB("#d75d9f"),
            600: toRGB("#c43e81"),
            700: toRGB("#a82e67"),
            800: toRGB("#8c2855"),
            900: toRGB("#75264a"),
            950: toRGB("#461129"),
          },
        },
        boxShadow: {
          "input-active": "0px 0px 0px 1px #FFF, 0px 0px 0px 2px #203637",
          "button-primary":
            "2px 2px 0px 0px var(--clr-bg-inv-acc-3, #415E63) inset",
          "button-primary-hover":
            "2px 2px 0px 0px var(--clr-bg-inv-acc-2, #4F747A) inset",
          "button-primary-focus":
            "0px 0px 0px 1px #FFF, 0px 0px 0px 2px var(--clr-border-def-sem-inf-1, #06AAF1), 2px 2px 0px 0px var(--clr-bg-inv-acc-2, #4F747A) inset",
          "button-primary-active":
            "0px 0px 0px 1px #FFF, 0px 0px 0px 2px var(--clr-bg-inv-acc-4, #203637), -2px -2px 0px 0px var(--clr-bg-inv-acc-1, #7B9B9F) inset",
          "button-secondary":
            "-2px -2px 0px 0px #CEDFE2 inset, 2px 2px 0px 0px white inset",
          "button-secondary-hover":
            "-2px -2px 0px 0px #CEDFE2 inset, 2px 2px 0px 0px #FFF inset",
          "button-secondary-focus":
            "0px 0px 0px 1px #FFF, 0px 0px 0px 2px var(--clr-border-def-sem-inf-1, #06AAF1), -2px -2px 0px 0px #CEDFE2 inset, 2px 2px 0px 0px #FFF inset",
          "button-secondary-active":
            "0px 0px 0px 1px white, 0px 0px 0px 2px var(--clr-bg-inv-acc-4, #203637), 2px 2px 0px 0px var(--clr-bg-inv-acc-2, #4F747A) inset",
        },
      },
    },
  }),
);
