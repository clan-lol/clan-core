import {
  MachineStatus,
  MachineStatusProps,
} from "@/src/components/MachineStatus/MachineStatus";
import { Meta, StoryObj } from "@kachurun/storybook-solid";

const meta: Meta<MachineStatusProps> = {
  title: "Components/MachineStatus",
  component: MachineStatus,
  decorators: [
    (Story: StoryObj) => (
      <div class="p-5 bg-inv-1">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<MachineStatusProps>;

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
