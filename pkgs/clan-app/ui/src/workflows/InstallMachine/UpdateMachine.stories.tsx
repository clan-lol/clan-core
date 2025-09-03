import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
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
import { UpdateModal } from "./UpdateMachine";

type ResultDataMap = {
  [K in OperationNames]: SuccessQuery<K>["data"];
};

const mockFetcher: Fetcher = <K extends OperationNames>(
  name: K,
  _args: unknown,
): ApiCall<K> => {
  // TODO: Make this configurable for every story
  const resultData: Partial<ResultDataMap> = {
    get_generators: [
      {
        name: "funny.gritty",
        prompts: [
          {
            name: "gritty.name",
            description: "Name of the gritty",
            prompt_type: "line",
            display: {
              helperText: null,
              label: "(1) Name",
              group: "User",
              required: true,
            },
          },
          {
            name: "gritty.foo",
            description: "Name of the gritty",
            prompt_type: "line",
            display: {
              helperText: null,
              label: "(2) Password",
              group: "Root",
              required: true,
            },
          },
          {
            name: "gritty.bar",
            description: "Name of the gritty",
            prompt_type: "line",
            display: {
              helperText: null,
              label: "(3) Gritty",
              group: "Root",
              required: true,
            },
          },
        ],
      },
      {
        name: "funny.dodo",
        prompts: [
          {
            name: "gritty.name",
            description: "Name of the gritty",
            prompt_type: "line",
            display: {
              helperText: null,
              label: "(4) Name",
              group: "User",
              required: true,
            },
          },
          {
            name: "gritty.foo",
            description: "Name of the gritty",
            prompt_type: "line",
            display: {
              helperText: null,
              label: "(5) Password",
              group: "Lonely",
              required: true,
            },
          },
          {
            name: "gritty.bar",
            description: "Name of the gritty",
            prompt_type: "line",
            display: {
              helperText: null,
              label: "(6) Batty",
              group: "Root",
              required: true,
            },
          },
        ],
      },
    ],
    run_generators: null,
    run_machine_update: null,
  };

  return {
    uuid: "mock",
    cancel: () => Promise.resolve(),
    result: new Promise((resolve) => {
      setTimeout(() => {
        const status = name === "run_machine_update" ? "error" : "success";

        resolve({
          op_key: "1",
          status: status,
          errors: [
            {
              message: "Mock error message",
              description:
                "This is a more detailed description of the mock error.",
            },
          ],
          data: resultData[name],
        } as OperationResponse<K>);
      }, 1500);
    }),
  };
};

const meta: Meta<typeof UpdateModal> = {
  title: "workflows/update",
  component: UpdateModal,
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

type Story = StoryObj<typeof UpdateModal>;

export const Init: Story = {
  description: "Welcome step for the update workflow",
  args: {
    open: true,
    machineName: "Jon",
  },
};
export const Address: Story = {
  description: "Welcome step for the update workflow",
  args: {
    open: true,
    machineName: "Jon",
    initialStep: "update:address",
  },
};
export const UpdateProgress: Story = {
  description: "Welcome step for the update workflow",
  args: {
    open: true,
    machineName: "Jon",
    initialStep: "update:progress",
  },
};
