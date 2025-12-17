import { MachineStatus } from "@/src/components/MachineStatus";
import { Meta, StoryObj } from "storybook-solidjs-vite";

const meta: Meta<typeof MachineStatus> = {
  title: "Components/MachineStatus",
  component: MachineStatus,
  decorators: [
    (Story) => (
      <div class="p-5 bg-inv-1">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Loading: Story = {
  args: {},
};

export const Online: Story = {
  args: {
    status: "online",
  },
};

export const Offline: Story = {
  args: {
    status: "offline",
  },
};

export const OutOfSync: Story = {
  args: {
    status: "out_of_sync",
  },
};

export const NotInstalled: Story = {
  args: {
    status: "not_installed",
  },
};

export const LoadingWithLabel: Story = {
  args: {
    ...Loading.args,
    label: true,
  },
};

export const OnlineWithLabel: Story = {
  args: {
    ...Online.args,
    label: true,
  },
};

export const OfflineWithLabel: Story = {
  args: {
    ...Offline.args,
    label: true,
  },
};

export const InstalledWithLabel: Story = {
  args: {
    ...OutOfSync.args,
    label: true,
  },
};

export const NotInstalledWithLabel: Story = {
  args: {
    ...NotInstalled.args,
    label: true,
  },
};
