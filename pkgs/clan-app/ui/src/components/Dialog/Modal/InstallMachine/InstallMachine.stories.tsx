import type { Meta, StoryObj } from "storybook-solidjs-vite";
import { InstallModal } from ".";
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
    get_system_file: ["id_rsa.pub"],
    list_system_storage_devices: {
      blockdevices: [
        {
          name: "sda_bla_bla",
          path: "/dev/sda",
          id_link: "usb-bla-bla",
          size: "12gb",
        },
        {
          name: "sdb_foo_foo",
          path: "/dev/sdb",
          id_link: "usb-boo-foo",
          size: "16gb",
        },
      ] as SuccessQuery<"list_system_storage_devices">["data"]["blockdevices"],
    },
    get_machine_disk_schemas: {
      "single-disk": {
        readme: "This is a single disk installation schema",
        frontmatter: {
          description: "Single disk installation schema",
        },
        name: "single-disk",
        placeholders: {
          mainDisk: {
            label: "Main Disk",
            required: true,
            options: ["disk1", "usb1"],
          },
        },
      },
    },
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
            prompt_type: "hidden",
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
            prompt_type: "hidden",
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
    get_machine_hardware_summary: {
      hardware_config: "nixos-facter",
      platform: "x86_64-linux",
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

const meta: Meta<typeof InstallModal> = {
  title: "workflows/install",
  component: InstallModal,
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

type Story = StoryObj<typeof meta>;

export const Init: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "init",
  },
};
export const CreateInstallerProse: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "create:prose",
  },
};
export const CreateInstallerImage: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "create:image",
  },
};
export const CreateInstallerDisk: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "create:disk",
  },
};
export const CreateInstallerProgress: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "create:progress",
  },
};
export const CreateInstallerDone: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "create:done",
  },
};
export const InstallConfigureAddress: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "install:address",
  },
};
export const InstallCheckHardware: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "install:check-hardware",
  },
};
export const InstallSelectDisk: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "install:disk",
  },
};
export const InstallVars: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "install:data",
  },
};
export const InstallSummary: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "install:summary",
  },
};
export const InstallProgress: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "install:progress",
  },
};
export const InstallDone: Story = {
  args: {
    open: true,
    machineName: "Test Machine",
    initialStep: "install:done",
  },
};
