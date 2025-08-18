import plugin from "tailwindcss/plugin";
// @ts-expect-error: lib of tailwind has no types
import { parseColor } from "tailwindcss/lib/util/color";
import { CSSRuleObject, RecursiveKeyValuePair } from "tailwindcss/types/config";

/* Converts HEX color to RGB */
const toRGB = (value: string) =>
  "rgb(" + parseColor(value).color.join(" ") + ")";

const primaries = {
  off: {
    white: toRGB("#ffffff"),
    black: toRGB("#000000"),
    toolbar_border: toRGB("#2e4a4b"),
  },
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
    50: toRGB("#f7f9fa"),
    100: toRGB("#e7f2f4"),
    200: toRGB("#d8e8eb"),
    300: toRGB("#afc6ca"),
    400: toRGB("#90b2b7"),
    500: toRGB("#7b9b9f"),
    600: toRGB("#4f747a"),
    700: toRGB("#415e63"),
    800: toRGB("#446065"),
    900: toRGB("#2c4347"),
    950: toRGB("#0d1416"),
  },
  error: {
    50: toRGB("#fff0f4"),
    100: toRGB("#ffe2ea"),
    200: toRGB("#ffcadb"),
    300: toRGB("#ff9fbd"),
    400: toRGB("#ff699b"),
    500: toRGB("#ff2c78"),
    600: toRGB("#ed116b"),
    700: toRGB("#c8085b"),
    800: toRGB("#a80953"),
    900: toRGB("#8f0c4d"),
    950: toRGB("#500126"),
  },
  info: {
    50: toRGB("#eff9ff"),
    100: toRGB("#d6ebff"),
    200: toRGB("#b5deff"),
    300: toRGB("#83cbff"),
    400: toRGB("#48adff"),
    500: toRGB("#1e88ff"),
    600: toRGB("#0666ff"),
    700: toRGB("#0051ff"),
    800: toRGB("#083fc5"),
    900: toRGB("#0d3a9b"),
    950: toRGB("#0e245d"),
  },
  success: {
    50: toRGB("#eefff3"),
    100: toRGB("#d7ffe4"),
    200: toRGB("#b2ffcb"),
    300: toRGB("#76ffa4"),
    400: toRGB("#34f475"),
    500: toRGB("#0ae856"),
    600: toRGB("#01b83f"),
    700: toRGB("#059035"),
    800: toRGB("#0a712e"),
    900: toRGB("#0b5c29"),
    950: toRGB("#003414"),
  },
  warning: {
    50: toRGB("#feffe4"),
    100: toRGB("#faffc4"),
    200: toRGB("#faffc4"),
    300: toRGB("#e8ff50"),
    400: toRGB("#d4ff00"),
    500: toRGB("#b9e600"),
    600: toRGB("#90b800"),
    700: toRGB("#6c8b00"),
    800: toRGB("#556d07"),
    900: toRGB("#485c0b"),
    950: toRGB("#253400"),
  },
};

const colorSystem = {
  bg: {
    def: {
      1: primaries.off.white,
      2: primaries.secondary["50"],
      3: primaries.secondary["100"],
      4: primaries.secondary["200"],
      acc: {
        1: primaries.primary["50"],
        2: primaries.secondary["100"],
        3: primaries.secondary["200"],
        4: primaries.secondary["300"],
      },
    },
    semantic: {
      error: {
        1: primaries.error["50"],
        2: primaries.error["100"],
        3: primaries.error["200"],
        4: primaries.error["300"],
      },
      info: {
        1: primaries.info["50"],
        2: primaries.info["100"],
        3: primaries.info["200"],
        4: primaries.info["300"],
      },
      success: {
        1: primaries.success["50"],
        2: primaries.success["100"],
        3: primaries.success["200"],
        4: primaries.success["300"],
      },
      warning: {
        1: primaries.warning["50"],
        2: primaries.warning["100"],
        3: primaries.warning["200"],
        4: primaries.warning["300"],
      },
    },
    inv: {
      1: primaries.primary["600"],
      2: primaries.primary["700"],
      3: primaries.primary["800"],
      4: primaries.primary["900"],
      acc: {
        1: primaries.secondary["500"],
        2: primaries.secondary["600"],
        3: primaries.secondary["900"],
        4: primaries.secondary["950"],
      },
    },
  },
  border: {
    def: {
      1: primaries.secondary["100"],
      2: primaries.secondary["200"],
      3: primaries.secondary["300"],
      4: primaries.secondary["400"],
      acc: {
        1: primaries.secondary["500"],
        2: primaries.secondary["900"],
        3: primaries.secondary["900"],
        4: primaries.secondary["950"],
      },
    },
    semantic: {
      error: {
        1: primaries.error["100"],
        2: primaries.error["200"],
        3: primaries.error["300"],
        4: primaries.error["400"],
      },
      info: {
        1: primaries.info["100"],
        2: primaries.info["200"],
        3: primaries.info["300"],
        4: primaries.info["400"],
      },
      success: {
        1: primaries.success["100"],
        2: primaries.success["200"],
        3: primaries.success["300"],
        4: primaries.success["400"],
      },
      warning: {
        1: primaries.warning["100"],
        2: primaries.warning["200"],
        3: primaries.warning["300"],
        4: primaries.warning["400"],
      },
    },
    inv: {
      1: primaries.secondary["700"],
      2: primaries.secondary["800"],
      3: primaries.secondary["900"],
      4: primaries.secondary["950"],
      acc: {
        1: primaries.secondary["300"],
        2: primaries.secondary["200"],
        3: primaries.secondary["100"],
        4: primaries.secondary["50"],
      },
    },
  },
  fg: {
    def: {
      1: primaries.secondary["950"],
      2: primaries.secondary["900"],
      3: primaries.secondary["700"],
      4: primaries.secondary["600"],
    },
    inv: {
      1: primaries.off.white,
      2: primaries.secondary["100"],
      3: primaries.secondary["300"],
      4: primaries.secondary["400"],
    },
    semantic: {
      error: {
        1: primaries.error["500"],
        2: primaries.error["600"],
        3: primaries.error["700"],
        4: primaries.error["800"],
      },
      info: {
        1: primaries.info["500"],
        2: primaries.info["600"],
        3: primaries.info["700"],
        4: primaries.info["800"],
      },
      success: {
        1: primaries.success["500"],
        2: primaries.success["600"],
        3: primaries.success["700"],
        4: primaries.success["800"],
      },
      warning: {
        1: primaries.warning["500"],
        2: primaries.warning["600"],
        3: primaries.warning["700"],
        4: primaries.warning["800"],
      },
    },
  },
};

function isString(value: unknown): value is string {
  return typeof value === "string";
}

const mkColorUtil = (
  path: string[],
  property: string,
  config: string | RecursiveKeyValuePair,
): CSSRuleObject => {
  if (isString(config)) {
    return {
      [`.${path.join("-")}`]: {
        [`${property}`]: config,
      },
    };
  }

  return Object.entries(config as RecursiveKeyValuePair)
    .map(([subKey, subConfig]) =>
      mkColorUtil([...path, subKey], property, subConfig),
    )
    .reduce((acc, curr) => ({ ...acc, ...curr }), {});
};

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

      const { bg, fg, border } = colorSystem;

      addUtilities(mkColorUtil(["bg"], "backgroundColor", bg));
      addUtilities(mkColorUtil(["fg"], "color", fg));
      addUtilities(mkColorUtil(["border"], "borderColor", border));
      addUtilities(mkColorUtil(["border-t"], "borderTop", border));
      addUtilities(mkColorUtil(["border-r"], "borderRight", border));
      addUtilities(mkColorUtil(["border-b"], "borderBottom", border));
      addUtilities(mkColorUtil(["border-l"], "borderLeft", border));

      // re-use the border colors for outline colors
      addUtilities(mkColorUtil(["outline"], "outlineColor", border));
      addUtilities(mkColorUtil(["outline-t"], "outlineTop", border));
      addUtilities(mkColorUtil(["outline-r"], "outlineRight", border));
      addUtilities(mkColorUtil(["outline-b"], "outlineBottom", border));
      addUtilities(mkColorUtil(["outline-l"], "outlineLeft", border));
    },
  // add configuration which is merged with the final config
  () => ({
    theme: {
      extend: {
        colors: {
          ...primaries,
          ...colorSystem,
        },
      },
    },
  }),
);
