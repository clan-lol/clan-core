import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import {
  createMemoryHistory,
  MemoryRouter,
  Route,
  RouteSectionProps,
} from "@solidjs/router";
import { Sidebar } from "@/src/components/Sidebar/Sidebar";
import { Suspense } from "solid-js";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";
import { addClanURI, resetStore } from "@/src/stores/clan";
import { SolidQueryDevtools } from "@tanstack/solid-query-devtools";
import { encodeBase64 } from "@/src/hooks/clan";
import { ApiClientProvider } from "@/src/hooks/ApiClient";
import {
  ApiCall,
  OperationArgs,
  OperationNames,
  OperationResponse,
} from "@/src/hooks/api";

const defaultClanURI = "/home/brian/clans/my-clan";

const queryData = {
  "/home/brian/clans/my-clan": {
    details: {
      name: "Brian's Clan",
      uri: "/home/brian/clans/my-clan",
    },
    machines: {
      europa: {
        name: "Europa",
        machineClass: "nixos",
      },
      ganymede: {
        name: "Ganymede",
        machineClass: "nixos",
      },
    },
  },
  "/home/brian/clans/davhau": {
    details: {
      name: "Dave's Clan",
      uri: "/home/brian/clans/davhau",
    },
    machines: {
      callisto: {
        name: "Callisto",
        machineClass: "nixos",
      },
      amalthea: {
        name: "Amalthea",
        machineClass: "nixos",
      },
    },
  },
  "/home/brian/clans/mic92": {
    details: {
      name: "Mic92's Clan",
      uri: "/home/brian/clans/mic92",
    },
    machines: {
      thebe: {
        name: "Thebe",
        machineClass: "nixos",
      },
      sponde: {
        name: "Sponde",
        machineClass: "nixos",
      },
    },
  },
};

const staticSections = [
  {
    title: "Links",
    links: [
      { label: "GitHub", path: "https://github.com/brian-the-dev" },
      { label: "Twitter", path: "https://twitter.com/brian_the_dev" },
      {
        label: "LinkedIn",
        path: "https://www.linkedin.com/in/brian-the-dev/",
      },
      {
        label: "Instagram",
        path: "https://www.instagram.com/brian_the_dev/",
      },
    ],
  },
];

const meta: Meta<RouteSectionProps> = {
  title: "Components/Sidebar",
  component: Sidebar,
  render: () => {
    // set history to point to our test clan
    const history = createMemoryHistory();
    history.set({ value: `/clans/${encodeBase64(defaultClanURI)}` });

    // reset local storage and then add each clan
    resetStore();

    Object.keys(queryData).forEach((uri) => addClanURI(uri));

    return (
      <div style="height: 670px;">
        <MemoryRouter
          history={history}
          root={(props) => <Suspense>{props.children}</Suspense>}
        >
          <Route
            path="/clans/:clanURI"
            component={() => <Sidebar staticSections={staticSections} />}
          >
            <Route path="/" />
            <Route
              path="/machines/:machineID"
              component={() => <h1>Machine</h1>}
            />
          </Route>
        </MemoryRouter>
        <SolidQueryDevtools initialIsOpen={true} />
      </div>
    );
  },
};

export default meta;

type Story = StoryObj<RouteSectionProps>;

const mockFetcher = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
) =>
  ({
    uuid: "mock",
    result: Promise.reject<OperationResponse<K>>("not implemented"),
    cancel: async () => {
      throw new Error("not implemented");
    },
  }) satisfies ApiCall<K>;

export const Default: Story = {
  args: {},
  decorators: [
    (Story: StoryObj) => {
      const queryClient = new QueryClient({
        defaultOptions: {
          queries: {
            retry: false,
            staleTime: Infinity,
          },
        },
      });

      Object.entries(queryData).forEach(([clanURI, clan]) => {
        queryClient.setQueryData(
          ["clans", encodeBase64(clanURI), "details"],
          clan.details,
        );
        queryClient.setQueryData(
          ["clans", encodeBase64(clanURI), "machines"],
          clan.machines || {},
        );
      });

      return (
        <ApiClientProvider client={{ fetch: mockFetcher }}>
          <QueryClientProvider client={queryClient}>
            <Story />
          </QueryClientProvider>
        </ApiClientProvider>
      );
    },
  ],
};
