import { Meta, StoryObj } from "storybook-solidjs-vite";

import { TagSelect } from "./TagSelect";
import { Tag } from "../Tag/Tag";
import Icon from "../Icon/Icon";
import { createSignal } from "solid-js";

const meta: Meta<typeof TagSelect> = {
  title: "Components/Custom/SelectStepper",
  component: TagSelect,
};

export default meta;

interface Item {
  value: string;
  label: string;
}

type Story = StoryObj<typeof meta>;

const Item = (item: Item) => (
  <Tag
    inverted
    icon={(tag) => (
      <Icon icon={"Machine"} size="0.5rem" inverted={tag.inverted} />
    )}
  >
    {item.label}
  </Tag>
);
export const Default: Story = {
  args: {
    renderItem: Item,
    label: "Peer",
    options: [
      { value: "foo", label: "Foo" },
      { value: "bar", label: "Bar" },
      { value: "baz", label: "Baz" },
      { value: "qux", label: "Qux" },
      { value: "quux", label: "Quux" },
      { value: "corge", label: "Corge" },
      { value: "grault", label: "Grault" },
    ],
  },
  render: (args) => {
    const [state, setState] = createSignal<Item[]>([]);
    return (
      <TagSelect<Item>
        {...args}
        values={state()}
        onClick={() => {
          console.log("Clicked, current values:");
          setState(() => [
            { value: "baz", label: "Baz" },
            { value: "qux", label: "Qux" },
          ]);
        }}
      />
    );
  },
};
