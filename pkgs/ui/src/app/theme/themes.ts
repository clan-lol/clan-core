import { ThemeOptions, createTheme } from "@mui/material/styles";

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

export const darkTheme = createTheme({
  ...commonOptions,
  palette: {
    mode: "dark",
    background: {
      default: palette.neutral5.value,
      paper: palette.neutral20.value,
    },
    primary: {
      main: palette.green60.value,
    },
    secondary: {
      main: palette.green60.value,
    },
    error: {
      main: palette.red60.value,
    },
    warning: {
      main: palette.yellow60.value,
    },
    success: {
      main: palette.green60.value,
    },
    info: {
      main: palette.red60.value,
    },
  },
});

export const lightTheme = createTheme({
  ...commonOptions,
  palette: {
    mode: "light",
    background: {
      default: common.white.value,
      paper: palette.neutral98.value,
    },
    primary: {
      main: palette.green50.value,
    },
    secondary: {
      main: palette.green50.value,
    },
    error: {
      main: palette.red50.value,
    },
    warning: {
      main: palette.yellow50.value,
    },
    success: {
      main: palette.green50.value,
    },
    info: {
      main: palette.red50.value,
    },
  },
});
