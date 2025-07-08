import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
import { Fieldset, FieldsetProps } from "@/src/components/Form/Fieldset";
import cx from "classnames";
import { TextInput } from "@/src/components/Form/TextInput";
import { TextArea } from "@/src/components/Form/TextArea";
import { Checkbox } from "@/src/components/Form/Checkbox";
import { FieldProps } from "./Field";

const FieldsetExamples = (props: FieldsetProps) => (
  <div class="flex flex-col gap-8">
    <Fieldset {...props} />
    <Fieldset {...props} inverted={true} />
  </div>
);

const meta = {
  title: "Components/Form/Fieldset",
  component: FieldsetExamples,
  decorators: [
    (Story: StoryObj, context: StoryContext<FieldsetProps>) => {
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
} satisfies Meta<FieldsetProps>;

export default meta;

export type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    legend: "Signup",
    children: (props: FieldProps) => (
      <>
        <TextInput
          {...props}
          label="First Name"
          required={true}
          input={{ placeholder: "Ron" }}
        />
        <TextInput
          {...props}
          label="Last Name"
          required={true}
          input={{ placeholder: "Burgundy" }}
        />
        <TextArea
          {...props}
          label="Bio"
          input={{ placeholder: "Tell us a bit about yourself", rows: 8 }}
        />
        <Checkbox {...props} label="Accept Terms" required={true} />
      </>
    ),
  },
};

export const Horizontal: Story = {
  args: {
    ...Default.args,
    orientation: "horizontal",
  },
};

export const Vertical: Story = {
  args: {
    ...Default.args,
    orientation: "vertical",
  },
};

export const Disabled: Story = {
  args: {
    ...Default.args,
    disabled: true,
  },
};

export const Error: Story = {
  args: {
    legend: "Signup",
    error: "You must enter a First Name",
    children: (props: FieldProps) => (
      <>
        <TextInput
          {...props}
          label="First Name"
          required={true}
          validationState="invalid"
          input={{ placeholder: "Ron" }}
        />
        <TextInput
          {...props}
          label="Last Name"
          required={true}
          validationState="invalid"
          input={{ placeholder: "Burgundy" }}
        />
        <TextArea
          {...props}
          label="Bio"
          input={{ placeholder: "Tell us a bit about yourself", rows: 8 }}
        />
        <Checkbox
          {...props}
          label="Accept Terms"
          validationState="invalid"
          required={true}
        />
      </>
    ),
  },
};
