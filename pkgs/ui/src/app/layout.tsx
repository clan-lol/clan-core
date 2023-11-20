"use client";
import { Sidebar } from "@/components/sidebar";
import { tw } from "@/utils/tailwind";
import { CssBaseline, ThemeProvider, useMediaQuery } from "@mui/material";
import { StyledEngineProvider } from "@mui/material/styles";
import axios from "axios";
import localFont from "next/font/local";
import * as React from "react";
import { Toaster } from "react-hot-toast";
import "./globals.css";
import { darkTheme, lightTheme } from "./theme/themes";

import { ClanToolbar } from "@/components/clanToolbar";
import { WithAppState } from "@/components/hooks/useAppContext";

const roboto = localFont({
  src: [
    {
      path: "../fonts/truetype/Roboto-Regular.ttf",
      weight: "400",
      style: "normal",
    },
  ],
});

axios.defaults.baseURL = "http://localhost:2979";

// add negative margin for smooth transition to fill the space of the sidebar
const translate = tw`lg:-ml-64 -ml-14`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const userPrefersDarkmode = useMediaQuery("(prefers-color-scheme: dark)");

  const [showSidebar, setShowSidebar] = React.useState(true);

  return (
    <html lang="en">
      <head>
        <title>Clan.lol</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="Clan.lol - build your own network" />
        <link rel="icon" href="./favicon.ico" sizes="any" />
      </head>
      <StyledEngineProvider injectFirst>
        <ThemeProvider theme={userPrefersDarkmode ? darkTheme : lightTheme}>
          <body id="__next" className={roboto.className}>
            <CssBaseline />
            <Toaster />
            <WithAppState>
              <div className="flex h-screen overflow-hidden bg-neutral-95">
                <ThemeProvider theme={darkTheme}>
                  <Sidebar
                    show={showSidebar}
                    onClose={() => setShowSidebar(false)}
                  />
                </ThemeProvider>
                <div
                  className={tw`${
                    !showSidebar && translate
                  } flex h-full w-full flex-col overflow-y-scroll transition-[margin] duration-150 ease-in-out`}
                >
                  <ClanToolbar
                    isSidebarVisible={showSidebar}
                    handleSidebar={setShowSidebar}
                  />
                  <div className="px-1">
                    <div className="relative flex h-full flex-1 flex-col">
                      <main>{children}</main>
                    </div>
                  </div>
                </div>
              </div>
            </WithAppState>
          </body>
        </ThemeProvider>
      </StyledEngineProvider>
    </html>
  );
}
