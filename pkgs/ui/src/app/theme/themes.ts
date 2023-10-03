import { createTheme } from "@mui/material/styles";

import colors from "@clan/colors/colors.json";

export const darkTheme = createTheme({
  breakpoints: {
    values: {
      xs: 0,
      sm: 400,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
  palette: {
    mode: "dark",
  },
});

const { palette, common } = colors.ref;
export const lightTheme = createTheme({
  breakpoints: {
    values: {
      xs: 0,
      sm: 400,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
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
