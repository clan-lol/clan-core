import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { InstallModal } from "./install";

const meta: Meta = {
  title: "workflows/install",
  component: InstallModal,
};

export default meta;

type Story = StoryObj;

export const Default: Story = {
  args: {
    machineName: "Test Machine",
    initialStep: "create:iso-1",
  },
};
