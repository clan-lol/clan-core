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
    list_service_modules: {
      core_input_name: "clan-core",
      modules: [
        {
          usage_ref: { name: "Borgbackup", input: null },
          instance_refs: [],
          native: true,
          info: {
            manifest: {
              name: "Borgbackup",
              description: "This is module A",
            },
            roles: {
              client: null,
              server: null,
            },
          },
        },
        {
          usage_ref: { name: "Zerotier", input: "fublub" },
          instance_refs: [],
          native: false,
          info: {
            manifest: {
              name: "Zerotier",
              description: "This is module B",
            },
            roles: {
              peer: null,
              moon: null,
              controller: null,
            },
          },
        },
      ],
    },
    list_machines: {
      jon: {
        data: {
          name: "jon",
          tags: ["all", "nixos", "tag1"],
        },
      },
      sara: {
        data: {
          name: "sara",
          tags: ["all", "darwin", "tag2"],
        },
      },
      kyra: {
        data: {
          name: "kyra",
          tags: ["all", "darwin", "tag2"],
        },
      },
      leila: {
        data: {
          name: "leila",
          tags: ["all", "darwin", "tag2"],
        },
      },
    },
    list_tags: {
      options: ["desktop", "server", "full", "only", "streaming", "backup"],
      special: ["all", "nixos", "darwin"],
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

export const SelectRoleMembers: Story = {
  render: () => (
    <ServiceWorkflow
      handleSubmit={(instance) => {
        console.log("Submitted instance:", instance);
      }}
      onClose={() => {
        console.log("Closed");
      }}
      initialStep="select:members"
      initialStore={{
        currentRole: "peer",
      }}
    />
  ),
};
