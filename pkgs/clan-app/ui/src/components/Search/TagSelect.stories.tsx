import { Meta, StoryObj } from "@kachurun/storybook-solid";

import { TagSelect, TagSelectProps } from "./TagSelect";
import { Tag } from "../Tag/Tag";
import Icon from "../Icon/Icon";

const meta = {
  title: "Components/Custom/SelectStepper",
  component: TagSelect,
} satisfies Meta<TagSelectProps<string>>;

export default meta;

type Story = StoryObj<TagSelectProps<string>>;

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
