"use client";

import "./globals.css";
import localFont from "next/font/local";
import * as React from "react";
import {
  Button,
  CssBaseline,
  IconButton,
  ThemeProvider,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { ChangeEvent, useState } from "react";
import { Toaster } from "react-hot-toast";
import { StyledEngineProvider } from "@mui/material/styles";

import { darkTheme, lightTheme } from "./theme/themes";
import { Sidebar } from "@/components/sidebar";
import MenuIcon from "@mui/icons-material/Menu";
import Image from "next/image";
import { tw } from "@/utils/tailwind";
import axios from "axios";

import {
  AppContext,
  WithAppState,
  useAppState,
} from "@/components/hooks/useAppContext";
import Background from "@/components/background";
import { usePathname, redirect } from "next/navigation";

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

const AutoRedirectEffect = () => {
  const { isLoading, data } = useAppState();
  const pathname = usePathname();
  React.useEffect(() => {
    if (!isLoading && !data.isJoined && pathname !== "/") {
      redirect("/");
    }
  }, [isLoading, data, pathname]);
  return <></>;
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const userPrefersDarkmode = useMediaQuery("(prefers-color-scheme: dark)");
  const theme = useTheme();
  const is_small = useMediaQuery(theme.breakpoints.down("sm"));

  let [useDarkTheme, setUseDarkTheme] = useState(false);
  let [showSidebar, setShowSidebar] = useState(true);

  // If the screen is small, hide the sidebar
  React.useEffect(() => {
    if (is_small) {
      setShowSidebar(false);
    } else {
      setShowSidebar(true);
    }
  }, [is_small]);

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
            <Toaster />
            <WithAppState>
              <AppContext.Consumer>
                {(appState) => {
                  const showSidebarDerived = Boolean(
                    showSidebar &&
                      !appState.isLoading &&
                      appState.data.isJoined,
                  );
                  return (
                    <>
                      <Background />
                      <div className="flex h-screen overflow-hidden">
                        <Sidebar
                          show={showSidebarDerived}
                          onClose={() => setShowSidebar(false)}
                        />
                        <div
                          className={tw`${
                            !showSidebarDerived && translate
                          } flex h-full w-full flex-col overflow-y-scroll transition-[margin] duration-150 ease-in-out`}
                        >
                          <div className="static top-0 mb-2 py-2">
                            <div className="grid grid-cols-3">
                              <div className="col-span-1">
                                <IconButton
                                  hidden={true}
                                  onClick={() => setShowSidebar((c) => !c)}
                                >
                                  {!showSidebar && appState.data.isJoined && (
                                    <MenuIcon />
                                  )}
                                </IconButton>
                              </div>
                              <div className="col-span-1 block w-full bg-fixed text-center font-semibold text-white lg:hidden">
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
                            <div className="relative flex h-full flex-1 flex-col">
                              <main>
                                <AutoRedirectEffect />
                                <Button
                                  fullWidth
                                  onClick={() => {
                                    appState.setAppState((s) => ({
                                      ...s,
                                      isJoined: !s.isJoined,
                                    }));
                                  }}
                                >
                                  Toggle Joined
                                </Button>

                                {children}
                              </main>
                            </div>
                          </div>
                        </div>
                      </div>
                    </>
                  );
                }}
              </AppContext.Consumer>
            </WithAppState>
          </body>
        </ThemeProvider>
      </StyledEngineProvider>
    </html>
  );
}
