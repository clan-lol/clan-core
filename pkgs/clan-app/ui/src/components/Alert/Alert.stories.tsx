import type { Meta, StoryObj } from "storybook-solidjs-vite";
import { Alert, AlertProps } from "@/src/components/Alert/Alert";
import { expect, fn } from "storybook/test";

const AlertExamples = (props: AlertProps) => (
  <div class="grid w-fit grid-cols-2 gap-8">
    <div class="w-72">
      <Alert {...props} />
    </div>
    <div class="w-72">
      <Alert {...props} size="s" />
    </div>
    <div class="w-72">
      <Alert {...props} transparent />
    </div>
    <div class="w-72">
      <Alert {...props} size="s" transparent />
    </div>
  </div>
);

const meta: Meta<typeof AlertExamples> = {
  title: "Components/Alert",
  component: AlertExamples,
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Info: Story = {
  args: {
    type: "info",
    title: "Headline",
    onDismiss: undefined,
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
  },
  render(args) {
    return <Alert {...args} />;
  },
  play: async ({ canvas, userEvent, args }) => {
    await userEvent.click(canvas.getByRole("button"));
    await expect(args.onDismiss).toHaveBeenCalled();
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
