import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Button, ButtonProps } from "./Button";
import Icon from "../icon";

const meta: Meta<ButtonProps> = {
  title: "Components/Button",
  component: Button,
};

export default meta;

type Story = StoryObj<ButtonProps>;

const children = "click me";

export const Default: Story = {
  args: {
    children,
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

export const StartIcon: Story = {
  args: {
    ...Default.args,
    startIcon: <Icon size={12} icon="Flash" />,
  },
};

export const EndIcon: Story = {
  args: {
    ...Default.args,
    endIcon: <Icon size={12} icon="Flash" />,
  },
};
