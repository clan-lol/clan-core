import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import {
  RemoteForm,
  RemoteData,
  Machine,
  RemoteDataSource,
} from "./RemoteForm";
import { createSignal } from "solid-js";
import { QueryClient, QueryClientProvider } from "@tanstack/solid-query";

// Default values for the form
const defaultRemoteData: RemoteData = {
  address: "",
  user: "",
  command_prefix: "sudo",
  port: undefined,
  private_key: undefined,
  password: "",
  forward_agent: true,
  host_key_check: "strict",
  verbose_ssh: false,
  ssh_options: {},
  tor_socks: false,
};

// Sample data for populated form
const sampleRemoteData: RemoteData = {
  address: "example.com",
  user: "admin",
  command_prefix: "sudo",
  port: 22,
  private_key: undefined,
  password: "",
  forward_agent: true,
  host_key_check: "ask",
  verbose_ssh: false,
  ssh_options: {
    StrictHostKeyChecking: "no",
    UserKnownHostsFile: "/dev/null",
  },
  tor_socks: false,
};

// Sample machine data for testing
const sampleMachine: Machine = {
  name: "test-machine",
  flake: {
    identifier: "git+https://git.example.com/test-repo",
  },
};

// Create a query client for stories
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

// Interactive wrapper component for Storybook
const RemoteFormWrapper = (props: {
  initialData: RemoteData;
  disabled?: boolean;
  machine: Machine;
  field?: "targetHost" | "buildHost";
  queryFn?: (params: {
    name: string;
    flake: { identifier: string };
    field: string;
  }) => Promise<RemoteDataSource | null>;
  onSave?: (data: RemoteData) => void | Promise<void>;
  showSave?: boolean;
}) => {
  const [formData, setFormData] = createSignal(props.initialData);
  const [saveMessage, setSaveMessage] = createSignal("");

  return (
    <QueryClientProvider client={queryClient}>
      <div class="max-w-2xl p-6">
        <h2 class="mb-6 text-2xl font-bold">Remote Configuration</h2>
        <RemoteForm
          onInput={(newData) => {
            setFormData(newData);
            // Log changes for Storybook actions
            console.log("Form data changed:", newData);
          }}
          disabled={props.disabled}
          machine={props.machine}
          field={props.field}
          queryFn={props.queryFn}
          onSave={props.onSave}
          showSave={props.showSave}
        />

        {/* Display save message if present */}
        {saveMessage() && (
          <div class="mt-4 rounded bg-green-100 p-3 text-green-800">
            {saveMessage()}
          </div>
        )}

        {/* Display current form state */}
        <details class="mt-8">
          <summary class="cursor-pointer font-semibold">
            Current Form Data (Debug)
          </summary>
          <pre class="mt-2 overflow-auto rounded bg-gray-100 p-4 text-sm">
            {JSON.stringify(formData(), null, 2)}
          </pre>
        </details>
      </div>
    </QueryClientProvider>
  );
};

const meta: Meta<typeof RemoteFormWrapper> = {
  title: "Components/RemoteForm",
  component: RemoteFormWrapper,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component:
          "A form component for configuring remote SSH connection settings. Based on the Remote Python class with fields for address, authentication, and SSH options.",
      },
    },
  },
  argTypes: {
    disabled: {
      control: "boolean",
      description: "Disable all form inputs",
    },
    machine: {
      control: "object",
      description: "Machine configuration for API queries",
    },
    field: {
      control: "select",
      options: ["targetHost", "buildHost"],
      description: "Field type for API queries",
    },
    showSave: {
      control: "boolean",
      description: "Show or hide the save button",
    },
    onSave: {
      action: "saved",
      description: "Custom save handler function",
    },
  },
};

export default meta;

type Story = StoryObj<typeof RemoteFormWrapper>;

export const Empty: Story = {
  args: {
    initialData: defaultRemoteData,
    disabled: false,
    machine: sampleMachine,
    queryFn: async () => ({
      source: "inventory" as const,
      data: {
        address: "",
        user: "",
        command_prefix: "",
        port: undefined,
        private_key: undefined,
        password: "",
        forward_agent: false,
        host_key_check: 0,
        verbose_ssh: false,
        ssh_options: {},
        tor_socks: false,
      },
    }),
  },
  parameters: {
    docs: {
      description: {
        story:
          "Empty form with default values. All fields start empty except for boolean defaults.",
      },
    },
    test: {
      timeout: 30000,
    },
  },
};

export const Populated: Story = {
  args: {
    initialData: sampleRemoteData,
    disabled: false,
    machine: sampleMachine,
    queryFn: async () => ({
      source: "inventory" as const,
      data: sampleRemoteData,
    }),
  },
  parameters: {
    docs: {
      description: {
        story:
          "Form pre-populated with sample data showing all field types in use.",
      },
    },
    test: {
      timeout: 30000,
    },
  },
};

export const Disabled: Story = {
  args: {
    initialData: sampleRemoteData,
    disabled: true,
    machine: sampleMachine,
  },
  parameters: {
    docs: {
      description: {
        story: "All form fields in disabled state. Useful for read-only views.",
      },
    },
  },
};

// Advanced example with custom SSH options
const advancedRemoteData: RemoteData = {
  address: "192.168.1.100",
  user: "deploy",
  command_prefix: "doas",
  port: 2222,
  private_key: undefined,
  password: "",
  forward_agent: false,
  host_key_check: "none",
  verbose_ssh: true,
  ssh_options: {
    ConnectTimeout: "10",
    ServerAliveInterval: "60",
    ServerAliveCountMax: "3",
    Compression: "yes",
    TCPKeepAlive: "yes",
  },
  tor_socks: true,
};

export const NixManaged: Story = {
  args: {
    initialData: advancedRemoteData,
    disabled: false,
    machine: sampleMachine,
    queryFn: async () => ({
      source: "nix_machine" as const,
      data: advancedRemoteData,
    }),
  },
  parameters: {
    docs: {
      description: {
        story:
          "Configuration managed by Nix with advanced settings. Shows the locked state with unlock option.",
      },
    },
  },
};

export const HiddenSaveButton: Story = {
  args: {
    initialData: sampleRemoteData,
    disabled: false,
    machine: sampleMachine,
    showSave: false,
    queryFn: async () => ({
      source: "inventory" as const,
      data: sampleRemoteData,
    }),
  },
  parameters: {
    docs: {
      description: {
        story:
          "Form with the save button hidden. Useful when save functionality is handled externally.",
      },
    },
  },
};
