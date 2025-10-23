import type { Meta, StoryObj } from "storybook-solidjs-vite";
import cx from "classnames";
import {
  HostFileInput,
  HostFileInputProps,
} from "@/src/components/Form/HostFileInput";

const Examples = (props: HostFileInputProps) => (
  <div class="flex flex-col gap-8">
    <div class="flex flex-col gap-8 p-8">
      <HostFileInput {...props} />
      <HostFileInput {...props} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <HostFileInput {...props} inverted={true} />
      <HostFileInput {...props} inverted={true} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8">
      <HostFileInput {...props} orientation="horizontal" />
      <HostFileInput {...props} orientation="horizontal" size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <HostFileInput {...props} inverted={true} orientation="horizontal" />
      <HostFileInput
        {...props}
        inverted={true}
        orientation="horizontal"
        size="s"
      />
    </div>
  </div>
);

const meta: Meta<typeof Examples> = {
  title: "Components/Form/HostFileInput",
  component: Examples,
  decorators: [
    (Story, { args }) => {
      return (
        <div
          class={cx({
            "w-[600px]": (args.orientation || "vertical") == "vertical",
            "w-[1024px]": args.orientation == "horizontal",
            "bg-inv-acc-3": args.inverted,
          })}
        >
          <Story />
        </div>
      );
    },
  ],
};

export default meta;

export type Story = StoryObj<typeof meta>;

export const Bare: Story = {
  args: {
    placeholder: "e.g. 11/06/89",
  },
};

export const Label: Story = {
  args: {
    ...Bare.args,
    label: "DOB",
  },
};

export const Description: Story = {
  args: {
    ...Label.args,
    description: "The date you were born",
  },
};

export const Required: Story = {
  args: {
    ...Description.args,
    required: true,
  },
};

export const Tooltip: Story = {
  args: {
    ...Required.args,
    tooltip: "The day you came out of your momma",
  },
};

export const Icon: Story = {
  args: {
    ...Tooltip.args,
    icon: "Checkmark",
  },
};

export const Ghost: Story = {
  args: {
    ...Icon.args,
    ghost: true,
  },
};

export const Invalid: Story = {
  args: {
    ...Tooltip.args,
    validationState: "invalid",
  },
};

export const Disabled: Story = {
  args: {
    ...Icon.args,
    disabled: true,
  },
};

export const ReadOnly: Story = {
  args: {
    ...Icon.args,
    readOnly: true,
    defaultValue: "14/05/02",
  },
};
