"use client";

import "./globals.css";
import localFont from "next/font/local";
import * as React from "react";
import {
  CssBaseline,
  IconButton,
  ThemeProvider,
  useMediaQuery,
} from "@mui/material";
import { ChangeEvent, useState } from "react";

import { StyledEngineProvider } from "@mui/material/styles";

import { darkTheme, lightTheme } from "./theme/themes";
import { Sidebar } from "@/components/sidebar";
import MenuIcon from "@mui/icons-material/Menu";
import { ChevronLeft } from "@mui/icons-material";
import Image from "next/image";

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
  const userPrefersDarkmode = useMediaQuery("(prefers-color-scheme: dark)");
  let [useDarkTheme, setUseDarkTheme] = useState(false);
  let [showSidebar, setShowSidebar] = useState(true);
  React.useEffect(() => {
    if (useDarkTheme !== userPrefersDarkmode) {
      // Enable dark theme if the user prefers dark mode
      setUseDarkTheme(userPrefersDarkmode);
    }
  }, [userPrefersDarkmode, useDarkTheme, setUseDarkTheme]);

  const changeThemeHandler = (target: ChangeEvent, currentValue: boolean) => {
    setUseDarkTheme(currentValue);
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
        <ThemeProvider theme={useDarkTheme ? darkTheme : lightTheme}>
          <body id="__next" className={roboto.className}>
            <CssBaseline />
            <div className="flex h-screen overflow-hidden">
              <Sidebar
                show={showSidebar}
                onClose={() => setShowSidebar(false)}
              />
              <div className="flex flex-col w-full h-full">
                <div className="static min-h-10 top-0 mb-2 py-2">
                  <div className="grid grid-cols-3">
                    <div className="col-span-1">
                      <IconButton
                        hidden={true}
                        onClick={() => setShowSidebar((c) => !c)}
                      >
                        {!showSidebar && <MenuIcon />}
                      </IconButton>
                    </div>
                    <div className="col-span-1 block lg:hidden w-full text-center font-semibold text-white ">
                      <Image
                        src="/logo.svg"
                        alt="Clan Logo"
                        width={58}
                        height={58}
                        priority
                      />
                    </div>
                  </div>
                </div>

                <div className="px-1">
                  <div className="relative flex flex-1 flex-col overflow-y-auto overflow-x-hidden">
                    <main>{children}</main>
                  </div>
                </div>
              </div>
            </div>
          </body>
        </ThemeProvider>
      </StyledEngineProvider>
    </html>
  );
}
