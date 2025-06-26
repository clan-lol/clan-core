import meta, { Story } from "./TextField.stories";

const checkboxMeta = {
  ...meta,
  title: "Components/Form/Fields/Checkbox",
};

export default checkboxMeta;

export const Bare: Story = {
  args: {
    type: "checkbox",
  },
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
    checkbox: {
      ...Tooltip.args.checkbox,
      defaultChecked: true,
    },
  },
};
