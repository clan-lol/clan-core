import type { Meta, StoryObj } from "storybook-solidjs-vite";
import cx from "classnames";
import { Checkbox, CheckboxProps } from "@/src/components/Form/Checkbox";

const Examples = (props: CheckboxProps) => (
  <div class="flex flex-col gap-8">
    <div class="flex flex-col gap-8 p-8">
      <Checkbox {...props} />
      <Checkbox {...props} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <Checkbox {...props} inverted={true} />
      <Checkbox {...props} inverted={true} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8">
      <Checkbox {...props} orientation="horizontal" />
      <Checkbox {...props} orientation="horizontal" size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <Checkbox {...props} inverted={true} orientation="horizontal" />
      <Checkbox {...props} inverted={true} orientation="horizontal" size="s" />
    </div>
  </div>
);

const meta: Meta<typeof Examples> = {
  title: "Components/Form/Checkbox",
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
  args: {},
};

export const Label: Story = {
  args: {
    ...Bare.args,
    label: "Accept Terms",
  },
};

export const Description: Story = {
  args: {
    ...Label.args,
    description: "That stuff you never bother reading",
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
    tooltip:
      "Let people know how you got here, great achievements or obstacles overcome",
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
    ...Tooltip.args,
    disabled: true,
  },
};

export const ReadOnlyUnchecked: Story = {
  args: {
    ...Tooltip.args,
    readOnly: true,
    defaultChecked: false,
  },
};

export const ReadOnlyChecked: Story = {
  args: {
    ...Tooltip.args,
    readOnly: true,
    defaultChecked: true,
  },
};
