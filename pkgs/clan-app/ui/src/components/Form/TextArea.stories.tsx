import type { Meta, StoryObj } from "storybook-solidjs-vite";
import cx from "classnames";
import { TextArea, TextAreaProps } from "./TextArea";

const Examples = (props: TextAreaProps) => (
  <div class="flex flex-col gap-8">
    <div class="flex flex-col gap-8 p-8">
      <TextArea {...props} />
      <TextArea {...props} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <TextArea {...props} inverted={true} />
      <TextArea {...props} inverted={true} size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8">
      <TextArea {...props} orientation="horizontal" />
      <TextArea {...props} orientation="horizontal" size="s" />
    </div>
    <div class="flex flex-col gap-8 p-8 bg-inv-acc-3">
      <TextArea {...props} inverted={true} orientation="horizontal" />
      <TextArea {...props} inverted={true} orientation="horizontal" size="s" />
    </div>
  </div>
);

const meta: Meta<typeof Examples> = {
  title: "Components/Form/TextArea",
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
    input: {
      rows: 10,
      placeholder: "I like craft beer and long walks on the beach",
    },
  },
};

export const Label: Story = {
  args: {
    ...Bare.args,
    label: "Biography",
  },
};

export const Description: Story = {
  args: {
    ...Label.args,
    description: "Tell us about yourself",
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

export const ReadOnly: Story = {
  args: {
    ...Tooltip.args,
    readOnly: true,
    defaultValue:
      "Good evening. I'm Ron Burgundy, and this is what's happening in your world tonight. ",
  },
};

export const AutoResize: Story = {
  args: {
    label: "Auto-resizing TextArea",
    description:
      "This textarea automatically adjusts its height based on content",
    tooltip: "Try typing multiple lines to see it grow",
    autoResize: true,
    minRows: 2,
    maxRows: 10,
    input: {
      placeholder: "Start typing to see the textarea grow...",
    },
  },
};

export const AutoResizeNoMax: Story = {
  args: {
    label: "Auto-resize without max height",
    description: "This textarea grows indefinitely with content",
    autoResize: true,
    minRows: 3,
    input: {
      placeholder: "This will grow as much as needed...",
    },
  },
};
