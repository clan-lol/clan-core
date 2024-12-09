/* @refresh reload */
import { Portal, render } from "solid-js/web";
import { Navigate, RouteDefinition, Router } from "@solidjs/router";

import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";
import {
  MachineDetails,
  MachineListView,
  CreateMachine,
} from "./routes/machines";
import { Layout } from "./layout/layout";
import { ClanList, CreateClan, ClanDetails } from "./routes/clans";
import { Flash } from "./routes/flash/view";
import { HostList } from "./routes/hosts/view";
import { Welcome } from "./routes/welcome";
import { Toaster } from "solid-toast";
import { ModuleList } from "./routes/modules/list";
import { ModuleDetails } from "./routes/modules/details";
import { ModuleDetails as AddModule } from "./routes/modules/add";
import { ApiTester } from "./api_test";

export const client = new QueryClient();

const root = document.getElementById("app");

window.clan = window.clan || {};

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
  icon?: string;
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
    path: "/machines",
    label: "Machines",
    icon: "devices_other",
    children: [
      {
        path: "/",
        label: "Overview",
        component: () => <MachineListView />,
      },
      {
        path: "/create",
        label: "Create",
        component: () => <CreateMachine />,
      },
      {
        path: "/:id",
        label: "Details",
        hidden: true,
        component: () => <MachineDetails />,
      },
    ],
  },
  {
    path: "/clans",
    label: "Clans",
    icon: "groups",
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
    path: "/modules",
    label: "Modules",
    icon: "apps",
    children: [
      {
        path: "/",
        label: "App Store",
        component: () => <ModuleList />,
      },
      {
        path: "details/:id",
        label: "Details",
        hidden: true,
        component: () => <ModuleDetails />,
      },
      {
        path: "/add/:id",
        label: "Details",
        hidden: true,
        component: () => <AddModule />,
      },
    ],
  },
  {
    path: "/tools",
    label: "Tools",
    icon: "bolt",
    children: [
      {
        path: "/flash",
        label: "Clan Installer",
        component: () => <Flash />,
      },
      {
        path: "/hosts",
        label: "Local Hosts",
        component: () => <HostList />,
      },
    ],
  },
  {
    path: "/welcome",
    label: "",
    hidden: false,
    component: () => <Welcome />,
  },
  {
    path: "/api_testing",
    label: "api_testing",
    icon: "bolt",
    hidden: false,
    component: () => <ApiTester />,
  },
];

render(
  () => (
    <>
      <Portal mount={document.body}>
        <Toaster position="top-right" containerClassName="z-[9999]" />
      </Portal>
      <QueryClientProvider client={client}>
        <Router root={Layout}>{routes}</Router>
      </QueryClientProvider>
    </>
  ),
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  root!,
);
