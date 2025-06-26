import type { Meta, StoryContext, StoryObj } from "@kachurun/storybook-solid";
import { Fieldset, FieldsetProps } from "@/src/components/v2/Form/Fieldset";
import cx from "classnames";

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
    fields: [
      {
        type: "text",
        label: "First Name",
        required: true,
        control: { placeholder: "Ron" },
      },
      {
        type: "text",
        label: "Last Name",
        required: true,
        control: { placeholder: "Burgundy" },
      },
      {
        type: "textarea",
        label: "Bio",
        control: { placeholder: "Tell us a bit about yourself", rows: 8 },
      },
      {
        type: "checkbox",
        label: "Accept Terms & Conditions",
        required: true,
      },
    ],
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
    fields: [
      {
        type: "text",
        label: "First Name",
        required: true,
        invalid: true,
        control: { placeholder: "Ron" },
      },
      {
        type: "text",
        label: "Last Name",
        required: true,
        invalid: true,
        control: { placeholder: "Burgundy" },
      },
      {
        type: "textarea",
        label: "Bio",
        control: { placeholder: "Tell us a bit about yourself", rows: 8 },
      },
      {
        type: "checkbox",
        label: "Accept Terms & Conditions",
        invalid: true,
        required: true,
      },
    ],
  },
};
