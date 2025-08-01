import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { InstallModal } from "./InstallModal";
import { machine } from "os";

const meta: Meta = {
  title: "workflows/InstallModal",
  component: InstallModal,
};

export default meta;

type Story = StoryObj;

export const Default: Story = {
  args: {
    machineName: "Test Machine",
  },
};
