import meta, { Icon, Story } from "./TextField.stories";

const textAreaMeta = {
  ...meta,
  title: "Components/Form/TextArea",
};

export default textAreaMeta;

export const Bare: Story = {
  args: {
    type: "textarea",
    textarea: {
      input: {
        rows: 10,
        placeholder: "I like craft beer and long walks on the beach",
      },
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
    invalid: true,
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
    textarea: {
      ...Tooltip.args.textarea,
      defaultValue:
        "Good evening. I'm Ron Burgundy, and this is what's happening in your world tonight. ",
    },
  },
};
