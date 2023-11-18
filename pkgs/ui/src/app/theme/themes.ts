import {
  PaletteOptions,
  ThemeOptions,
  createTheme,
} from "@mui/material/styles";

import colors from "@clan/colors/colors.json";
const { palette, common } = colors.ref;

const commonOptions: Partial<ThemeOptions> = {
  breakpoints: {
    values: {
      xs: 0,
      sm: 400,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
};

const commonPalette: Partial<PaletteOptions> = {
  primary: {
    main: palette.blue50.value,
  },
  secondary: {
    main: palette.green60.value,
  },
  info: {
    main: palette.blue50.value,
  },
  success: {
    main: palette.green60.value,
  },
  warning: {
    main: palette.yellow80.value,
  },
  error: {
    main: palette.red50.value,
  },
};

export const darkTheme = createTheme({
  ...commonOptions,
  palette: {
    mode: "dark",
    ...commonPalette,
    background: {
      default: palette.neutral2.value,
      paper: palette.neutral5.value,
    },
    common: {
      black: common.black.value,
      white: common.white.value,
    },
  },
});

export const lightTheme = createTheme({
  ...commonOptions,
  palette: {
    mode: "light",
    ...commonPalette,
    background: {
      default: palette.neutral98.value,
      paper: palette.neutral100.value,
    },
  },
});
