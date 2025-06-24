import {
  MachineStatus,
  MachineStatusProps,
} from "@/src/components/v2/MachineStatus/MachineStatus";
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

export const Online: Story = {
  args: {
    status: "Online",
  },
};

export const Offline: Story = {
  args: {
    status: "Offline",
  },
};

export const Installed: Story = {
  args: {
    status: "Installed",
  },
};

export const NotInstalled: Story = {
  args: {
    status: "Not Installed",
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
    ...Installed.args,
    label: true,
  },
};

export const NotInstalledWithLabel: Story = {
  args: {
    ...NotInstalled.args,
    label: true,
  },
};
