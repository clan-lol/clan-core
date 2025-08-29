import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
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
        name: "pandora",
      },
      enceladus: {
        name: "enceladus",
      },
      dione: {
        name: "dione",
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
    (Story: StoryObj, context: StoryContext) => {
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
