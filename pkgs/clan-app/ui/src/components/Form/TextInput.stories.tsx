import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
import cx from "classnames";
import { TextInput, TextInputProps } from "@/src/components/Form/TextInput";
import Icon from "../Icon/Icon";
import { Button } from "@kobalte/core/button";

const Examples = (props: TextInputProps) => (
  <div class="flex flex-col gap-8">
    <div class="flex flex-col gap-8 p-8">
      <TextInput {...props} />
      <TextInput {...props} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <TextInput {...props} inverted={true} />
      <TextInput {...props} inverted={true} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8">
      <TextInput {...props} orientation="horizontal" />
      <TextInput {...props} orientation="horizontal" size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <TextInput {...props} inverted={true} orientation="horizontal" />
      <TextInput {...props} inverted={true} orientation="horizontal" size="s" />
    </div>
  </div>
);

const meta = {
  title: "Components/Form/TextInput",
  component: Examples,
  decorators: [
    (Story: StoryObj, context: StoryContext<TextInputProps>) => {
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
} satisfies Meta<TextInputProps>;

export default meta;

export type Story = StoryObj<typeof meta>;

export const Bare: Story = {
  args: {
    input: {
      placeholder: "e.g. 11/06/89",
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

export const WithIcon: Story = {
  args: {
    ...Tooltip.args,
    startComponent: () => <Icon icon="EyeClose" color="quaternary" inverted />,
  },
};

export const WithStartComponent: Story = {
  args: {
    ...Tooltip.args,
    startComponent: (props: { inverted?: boolean }) => (
      <Button>
        <Icon icon="EyeClose" color="quaternary" {...props} />
      </Button>
    ),
  },
};

export const WithEndComponent: Story = {
  args: {
    ...Tooltip.args,
    endComponent: (props: { inverted?: boolean }) => (
      <Button>
        <Icon icon="EyeOpen" color="quaternary" {...props} />
      </Button>
    ),
  },
};

export const Ghost: Story = {
  args: {
    ...WithIcon.args,
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
    ...WithIcon.args,
    disabled: true,
  },
};

export const ReadOnly: Story = {
  args: {
    ...WithIcon.args,
    readOnly: true,
    defaultValue: "14/05/02",
  },
};
