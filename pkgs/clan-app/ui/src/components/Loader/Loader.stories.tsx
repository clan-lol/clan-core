import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Loader, LoaderProps } from "@/src/components/Loader/Loader";

const meta: Meta<LoaderProps> = {
  title: "Components/Loader",
  component: Loader,
};

export default meta;

type Story = StoryObj<LoaderProps>;

export const Primary: Story = {
  args: {
    hierarchy: "primary",
  },
};

export const Secondary: Story = {
  args: {
    hierarchy: "secondary",
  },
};
