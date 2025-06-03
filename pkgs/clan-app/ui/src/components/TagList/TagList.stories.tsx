import type { Meta, StoryObj } from "@kachurun/storybook-solid";
import { TagList, TagListProps } from "./TagList";

const meta: Meta<TagListProps> = {
  title: "Components/TagList",
  component: TagList,
  decorators: [
    // wrap in a fixed width div so we can check that it wraps
    (Story) => {
      return (
        <div style={{ width: "20em" }}>
          <Story />
        </div>
      );
    },
  ],
};

export default meta;

type Story = StoryObj<TagListProps>;

export const Default: Story = {
  args: {
    values: [
      "Titan",
      "Enceladus",
      "Mimas",
      "Dione",
      "Iapetus",
      "Tethys",
      "Hyperion",
      "Epimetheus",
    ],
  },
};
