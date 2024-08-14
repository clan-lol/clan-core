/* @refresh reload */
import { render } from "solid-js/web";
import { RouteDefinition, Router } from "@solidjs/router";

import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";
import { MachineDetails } from "./routes/machines/[name]/view";
import { Layout } from "./layout/layout";
import { MachineListView } from "./routes/machines/view";
import { CreateClan } from "./routes/clan/view";
import { Settings } from "./routes/settings";
import { EditClanForm } from "./routes/clan/editClan";
import { Flash } from "./routes/flash/view";
import { CreateMachine } from "./routes/machines/create";
import { HostList } from "./routes/hosts/view";
import { Welcome } from "./routes/welcome";

const client = new QueryClient();

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
    path: "/clan",
    label: "Clans",
    icon: "groups",
    children: [
      {
        path: "/",
        label: "Overview",
        component: () => <Settings />,
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
    hidden: true,
    component: () => <Welcome />,
  },
];

render(
  () => (
    <QueryClientProvider client={client}>
      <Router root={Layout}>{routes}</Router>
    </QueryClientProvider>
  ),
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  root!,
);
