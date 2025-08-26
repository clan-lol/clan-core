import { Meta, StoryObj } from "@kachurun/storybook-solid";

import { SelectStepper, SelectStepperProps } from "./SelectStepper";
import { Tag } from "../Tag/Tag";
import Icon from "../Icon/Icon";

const meta = {
  title: "Components/Custom/SelectStepper",
  component: SelectStepper,
} satisfies Meta<SelectStepperProps<string>>;

export default meta;

type Story = StoryObj<SelectStepperProps<string>>;

const Item = (item: string) => (
  <Tag
    inverted
    icon={(tag) => (
      <Icon icon={"Machine"} size="0.5rem" inverted={tag.inverted} />
    )}
  >
    {item}
  </Tag>
);
export const Default: Story = {
  args: {
    renderItem: Item,
    values: ["foo", "bar"],
    options: ["foo", "bar", "baz", "qux", "quux"],
    onChange: (values: string[]) => {
      console.log("Selected values:", values);
    },
    onClick: () => {
      console.log("Combobox clicked");
    },
  },
};
