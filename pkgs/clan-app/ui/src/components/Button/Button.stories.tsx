import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Button, ButtonProps } from "./Button";
import FlashIcon from "@/icons/flash.svg";

const meta: Meta<ButtonProps> = {
  title: "Components/Button",
  component: Button,
};

export default meta;

type Story = StoryObj<ButtonProps>;

const children = "click me";
const startIcon = <FlashIcon width={16} height={16} viewBox="0 0 48 48" />;

export const Default: Story = {
  args: {
    children,
    startIcon,
  },
};

export const Small: Story = {
  args: {
    ...Default.args,
    size: "s",
  },
};

export const Light: Story = {
  args: {
    ...Default.args,
    variant: "light",
  },
};

export const Ghost: Story = {
  args: {
    ...Default.args,
    variant: "ghost",
  },
};
