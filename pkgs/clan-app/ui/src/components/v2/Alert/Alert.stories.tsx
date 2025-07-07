import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Alert, AlertProps } from "@/src/components/v2/Alert/Alert";
import { expect, fn } from "storybook/test";
import { StoryContext } from "@kachurun/storybook-solid-vite";

const meta: Meta<AlertProps> = {
  title: "Components/Alert",
  component: Alert,
  decorators: [
    (Story: StoryObj) => (
      <div class="w-72">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<AlertProps>;

export const Info: Story = {
  args: {
    type: "info",
    title: "Headline",
    description:
      "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
  },
};

export const Error: Story = {
  args: {
    ...Info.args,
    type: "error",
  },
};

export const Warning: Story = {
  args: {
    ...Info.args,
    type: "warning",
  },
};

export const Success: Story = {
  args: {
    ...Info.args,
    type: "success",
  },
};

export const InfoIcon: Story = {
  args: {
    ...Info.args,
    icon: "Info",
  },
};

export const ErrorIcon: Story = {
  args: {
    ...Error.args,
    icon: "WarningFilled",
  },
};

export const WarningIcon: Story = {
  args: {
    ...Warning.args,
    icon: "WarningFilled",
  },
};

export const SuccessIcon: Story = {
  args: {
    ...Success.args,
    icon: "Checkmark",
  },
};

export const InfoDismiss: Story = {
  args: {
    ...Info.args,
    onDismiss: fn(),
    play: async ({ canvas, step, userEvent, args }: StoryContext) => {
      await userEvent.click(canvas.getByRole("button"));
      await expect(args.onDismiss).toHaveBeenCalled();
    },
  },
};

export const ErrorDismiss: Story = {
  args: {
    ...InfoDismiss.args,
    type: "error",
  },
};

export const WarningDismiss: Story = {
  args: {
    ...InfoDismiss.args,
    type: "warning",
  },
};

export const SuccessDismiss: Story = {
  args: {
    ...InfoDismiss.args,
    type: "success",
  },
};

export const InfoIconDismiss: Story = {
  args: {
    ...InfoDismiss.args,
    icon: "Info",
  },
};

export const ErrorIconDismiss: Story = {
  args: {
    ...ErrorDismiss.args,
    icon: "WarningFilled",
  },
};

export const WarningIconDismiss: Story = {
  args: {
    ...WarningDismiss.args,
    icon: "WarningFilled",
  },
};

export const SuccessIconDismiss: Story = {
  args: {
    ...SuccessDismiss.args,
    icon: "Checkmark",
  },
};
