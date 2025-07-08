import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
import cx from "classnames";

import { Combobox, ComboboxProps } from "./Combobox";

const ComboboxExamples = (props: ComboboxProps<string>) => (
  <div class="flex flex-col gap-8">
    <div class="flex flex-col gap-8 p-8">
      <Combobox {...props} />
      <Combobox {...props} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <Combobox {...props} inverted={true} />
      <Combobox {...props} inverted={true} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8">
      <Combobox {...props} orientation="horizontal" />
      <Combobox {...props} orientation="horizontal" size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <Combobox {...props} inverted={true} orientation="horizontal" />
      <Combobox {...props} inverted={true} orientation="horizontal" size="s" />
    </div>
  </div>
);

const meta = {
  title: "Components/Form/Combobox",
  component: ComboboxExamples,
  decorators: [
    (Story: StoryObj, context: StoryContext<ComboboxProps<string>>) => {
      return (
        <div
          class={cx({
            "w-[600px]": (context.args.orientation || "vertical") == "vertical",
            "w-[1024px]": context.args.orientation == "horizontal",
            "bg-inv-acc-3": context.args.inverted,
          })}
        >
          <Story />
        </div>
      );
    },
  ],
} satisfies Meta<ComboboxProps<string>>;

export default meta;

export type Story = StoryObj<typeof meta>;

export const Bare: Story = {
  args: {
    options: ["foo", "bar", "baz"],
    defaultValue: "foo",
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

export const Multiple: Story = {
  args: {
    ...Description.args,
    required: true,
    multiple: true,
    defaultValue: ["foo", "bar"],
  },
};

export const Tooltip: Story = {
  args: {
    ...Required.args,
    tooltip: "The day you came out of your momma",
  },
};

export const Ghost: Story = {
  args: {
    ...Tooltip.args,
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
    ...Tooltip.args,
    disabled: true,
  },
};

export const MultipleDisabled: Story = {
  args: {
    ...Multiple.args,
    disabled: true,
  },
};

export const ReadOnly: Story = {
  args: {
    ...Tooltip.args,
    readOnly: true,
    defaultValue: "foo",
  },
};

export const MultipleReadonly: Story = {
  args: {
    ...Multiple.args,
    readOnly: true,
  },
};
