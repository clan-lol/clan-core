import type { Meta, StoryObj } from "storybook-solidjs-vite";
import { AddMachine } from "@/src/workflows/AddMachine/AddMachine";
import {
  createMemoryHistory,
  MemoryRouter,
  RouteDefinition,
} from "@solidjs/router";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";
import { ApiClientProvider, Fetcher } from "@/src/hooks/ApiClient";
import {
  ApiCall,
  OperationNames,
  OperationResponse,
  SuccessQuery,
} from "@/src/hooks/api";

type ResultDataMap = {
  [K in OperationNames]: SuccessQuery<K>["data"];
};

const mockFetcher: Fetcher = <K extends OperationNames>(
  name: K,
  _args: unknown,
): ApiCall<K> => {
  // TODO: Make this configurable for every story
  const resultData: Partial<ResultDataMap> = {
    list_machines: {
      pandora: {
        data: {
          name: "pandora",
          deploy: {
            buildHost: null,
            targetHost: null,
          },
          description: null,
          icon: null,
          installedAt: null,
          machineClass: "nixos",
          tags: [],
        },
      },
      enceladus: {
        data: {
          name: "enceladus",
          deploy: {
            buildHost: null,
            targetHost: null,
          },
          description: null,
          icon: null,
          installedAt: null,
          machineClass: "nixos",
          tags: [],
        },
      },
      dione: {
        data: {
          name: "dione",
          deploy: {
            buildHost: null,
            targetHost: null,
          },
          description: null,
          icon: null,
          installedAt: null,
          machineClass: "nixos",
          tags: [],
        },
      },
    },
  };

  return {
    uuid: "mock",
    cancel: () => Promise.resolve(),
    result: new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          op_key: "1",
          status: "success",
          data: resultData[name],
        } as OperationResponse<K>);
      }, 1500);
    }),
  };
};

const meta: Meta<typeof AddMachine> = {
  title: "workflows/add-machine",
  component: AddMachine,
  decorators: [
    (Story) => {
      const Routes: RouteDefinition[] = [
        {
          path: "/clans/:clanURI",
          component: () => (
            <div class="w-[600px]">
              <Story />
            </div>
          ),
        },
      ];

      const history = createMemoryHistory();
      history.set({ value: "/clans/dGVzdA==", replace: true });

      const queryClient = new QueryClient();

      return (
        <ApiClientProvider client={{ fetch: mockFetcher }}>
          <QueryClientProvider client={queryClient}>
            <MemoryRouter
              root={(props) => {
                console.debug("Rendering MemoryRouter root with props:", props);
                return props.children;
              }}
              history={history}
            >
              {Routes}
            </MemoryRouter>
          </QueryClientProvider>
        </ApiClientProvider>
      );
    },
  ],
};

export default meta;

type Story = StoryObj<typeof AddMachine>;

export const General: Story = {
  args: {},
};

export const Host: Story = {
  args: {
    initialStep: "host",
  },
};

export const Tags: Story = {
  args: {
    initialStep: "tags",
  },
};

export const Progress: Story = {
  args: {
    initialStep: "progress",
  },
};
