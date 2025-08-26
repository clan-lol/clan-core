import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
import { ServiceWorkflow } from "./Service";
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
    list_service_modules: [
      {
        module: { name: "Module A", input: "Input A" },
        info: {
          manifest: {
            name: "Module A",
            description: "This is module A",
          },
          roles: {
            peer: null,
            server: null,
          },
        },
      },
      {
        module: { name: "Module B", input: "Input B" },
        info: {
          manifest: {
            name: "Module B",
            description: "This is module B",
          },
          roles: {
            default: null,
          },
        },
      },
      {
        module: { name: "Module C", input: "Input B" },
        info: {
          manifest: {
            name: "Module B",
            description: "This is module B",
          },
          roles: {
            default: null,
          },
        },
      },
      {
        module: { name: "Module B", input: "Input A" },
        info: {
          manifest: {
            name: "Module B",
            description: "This is module B",
          },
          roles: {
            default: null,
          },
        },
      },
    ],
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

const meta: Meta<typeof ServiceWorkflow> = {
  title: "workflows/service",
  component: ServiceWorkflow,
  decorators: [
    (Story: StoryObj, context: StoryContext) => {
      const Routes: RouteDefinition[] = [
        {
          path: "/clans/:clanURI",
          component: () => (
            <div>
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

type Story = StoryObj<typeof ServiceWorkflow>;

export const Default: Story = {
  args: {},
};
