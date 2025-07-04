/* @refresh reload */
import { Portal, render } from "solid-js/web";
import { Navigate, RouteDefinition, Router } from "@solidjs/router";

import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";
import {
  CreateMachine,
  MachineDetails,
  MachineListView,
  MachineInstall,
} from "./routes/machines";
import { Layout } from "./layout/layout";
import { ClanDetails, ClanList, CreateClan } from "./routes/clans";
import { Flash } from "./routes/flash/view";
import { Welcome } from "./routes/welcome";
import { Toaster } from "solid-toast";
import { ModuleList } from "./routes/modules/list";
import { ModuleDetails } from "./routes/modules/details";
import { ModuleDetails as AddModule } from "./routes/modules/add";
import { ApiTester } from "./api_test";
import { IconVariant } from "./components/icon";
import { VarsPage } from "./routes/machines/install/vars-step";
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
    path: "/machines",
    label: "Machines",
    icon: "Grid",
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
      {
        path: "/:id/vars",
        label: "Vars",
        hidden: true,
        component: () => <VarsPage />,
      },
      {
        path: "/:id/install",
        label: "Install",
        hidden: true,
        component: () => <MachineInstall />,
      },
    ],
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
    path: "/modules",
    label: "Modules",
    icon: "Search",
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
    icon: "Folder",
    children: [
      {
        path: "/flash",
        label: "Flash Installer",
        component: () => <Flash />,
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
        path: "/api_testing",
        label: "api_testing",
        hidden: false,
        component: () => <ApiTester />,
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
