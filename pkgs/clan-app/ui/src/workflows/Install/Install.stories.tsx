import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { InstallModal } from "./install";

const meta: Meta = {
  title: "workflows/install",
  component: InstallModal,
};

export default meta;

type Story = StoryObj;

export const Init: Story = {
  description: "Welcome step for the installation workflow",
  args: {
    machineName: "Test Machine",
    initialStep: "init",
  },
};
export const CreateInstallerProse: Story = {
  description: "Prose step for creating an installer",
  args: {
    machineName: "Test Machine",
    initialStep: "create:prose",
  },
};
export const CreateInstallerImage: Story = {
  description: "Configure the image to install",
  args: {
    machineName: "Test Machine",
    initialStep: "create:image",
  },
};
export const CreateInstallerDisk: Story = {
  description: "Select a disk to install the image on",
  args: {
    machineName: "Test Machine",
    initialStep: "create:disk",
  },
};
