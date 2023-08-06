"use client";

import "./globals.css";
import localFont from "next/font/local";
import * as React from "react";
import { CssBaseline, ThemeProvider } from "@mui/material";
import { ChangeEvent, useState } from "react";

import { StyledEngineProvider } from "@mui/material/styles";

import { darkTheme, lightTheme } from "./theme/themes";
import { Sidebar } from "@/components/sidebar";

const roboto = localFont({
  src: [
    {
      path: "../fonts/truetype/Roboto-Regular.ttf",
      weight: "400",
      style: "normal",
    },
  ],
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let [useDarkTheme, setUseDarkTheme] = useState(false);
  let [theme, setTheme] = useState(useDarkTheme ? darkTheme : lightTheme);

  const changeThemeHandler = (target: ChangeEvent, currentValue: boolean) => {
    setUseDarkTheme(currentValue);
    setTheme(currentValue ? darkTheme : lightTheme);
  };

  return (
    <html lang="en">
      <head>
        <title>Clan.lol</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="Clan.lol - build your own network" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <StyledEngineProvider injectFirst>
        <ThemeProvider theme={theme}>
          <body id="__next" className={roboto.className}>
            <CssBaseline />
            <div className="flex h-screen overflow-hidden">
              <Sidebar />
              <div className="relative flex flex-1 flex-col overflow-y-auto overflow-x-hidden">
                <main>{children}</main>
              </div>
            </div>
          </body>
        </ThemeProvider>
      </StyledEngineProvider>
    </html>
  );
}
