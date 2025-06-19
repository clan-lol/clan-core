/* @refresh reload */
import { Portal, render } from "solid-js/web";
import { Navigate, RouteDefinition, Router } from "@solidjs/router";

import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";

import { Layout } from "./layout/layout";
import { ClanDetails, ClanList, CreateClan } from "./routes/clans";
import { HostList } from "./routes/hosts/view";
import { Welcome } from "./routes/welcome";
import { Toaster } from "solid-toast";
import { ApiTester } from "./api_test";
import { IconVariant } from "./components/icon";
import { Components } from "./routes/components";
import { ThreePlayground } from "./three";
import { ClanProvider } from "./contexts/clan";

export const client = new QueryClient();

const root = document.getElementById("app");

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    "Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?",
  );
}
if (import.meta.env.DEV) {
  console.log("Development mode");
  // Load the debugger in development mode
  await import("solid-devtools");
}

export type AppRoute = Omit<RouteDefinition, "children"> & {
  label: string;
  icon?: IconVariant;
  children?: AppRoute[];
  hidden?: boolean;
};

export const routes: AppRoute[] = [
  {
    path: "/",
    label: "",
    hidden: true,
    component: () => <Navigate href="/machines" />,
  },

  {
    path: "/clans",
    label: "Clans",
    hidden: true,
    icon: "List",
    children: [
      {
        path: "/",
        label: "Overview",
        component: () => <ClanList />,
      },
      {
        path: "/create",
        label: "Create",
        component: () => <CreateClan />,
      },
      {
        path: "/:id",
        label: "Details",
        hidden: true,
        component: () => <ClanDetails />,
      },
    ],
  },

  {
    path: "/welcome",
    label: "",
    hidden: true,
    component: () => <Welcome />,
  },
  {
    path: "/internal-dev",
    label: "Internal (Only visible in dev mode)",
    children: [
      {
        path: "/hosts",
        label: "Local Hosts",
        component: () => <HostList />,
      },
      {
        path: "/3d",
        label: "3D-Playground",
        component: () => <ThreePlayground />,
      },
      {
        path: "/api_testing",
        label: "api_testing",
        hidden: false,
        component: () => <ApiTester />,
      },
      {
        path: "/components",
        label: "Components",
        hidden: false,
        component: () => <Components />,
      },
    ],
  },
];

render(
  () => (
    <>
      <Portal mount={document.body}>
        <Toaster position="top-right" containerClassName="z-[9999]" />
      </Portal>
      <QueryClientProvider client={client}>
        <ClanProvider>
          <Router root={Layout}>{routes}</Router>
        </ClanProvider>
      </QueryClientProvider>
    </>
  ),
  root!,
);
