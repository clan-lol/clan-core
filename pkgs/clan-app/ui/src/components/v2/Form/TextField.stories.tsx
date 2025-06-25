import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
import { Field, FieldProps } from "./Field";
import cx from "classnames";

const FieldExamples = (props: FieldProps) => (
  <div class="flex flex-col gap-8">
    <div class="flex flex-col gap-8 p-8">
      <Field {...props} />
      <Field {...props} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <Field {...props} inverted={true} />
      <Field {...props} inverted={true} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8">
      <Field {...props} orientation="horizontal" />
      <Field {...props} orientation="horizontal" size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <Field {...props} inverted={true} orientation="horizontal" />
      <Field {...props} inverted={true} orientation="horizontal" size="s" />
    </div>
  </div>
);

const meta = {
  title: "Components/Form/TextField",
  component: FieldExamples,
  decorators: [
    (Story: StoryObj, context: StoryContext<FieldProps>) => {
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
} satisfies Meta<FieldProps>;

export default meta;

export type Story = StoryObj<typeof meta>;

export const Bare: Story = {
  args: {
    type: "text",
    text: {
      input: {
        placeholder: "e.g. 11/06/89",
      },
    },
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
    invalid: true,
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
    text: {
      defaultValue: "14/05/02",
    },
  },
};
