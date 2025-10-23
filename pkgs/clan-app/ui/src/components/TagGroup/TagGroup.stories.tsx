import { TagGroup } from "@/src/components/TagGroup/TagGroup";
import { Meta, StoryObj } from "storybook-solidjs-vite";

const meta: Meta<typeof TagGroup> = {
  title: "Components/TagGroup",
  component: TagGroup,
  decorators: [
    (Story) => (
      /* for some reason w-x from tailwind was not working */
      <div style="width: 196px">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    labels: [
      "Tag 1",
      "Tag 2",
      "Tag 3",
      "Tag 4",
      "Tag 5",
      "Tag 6",
      "Tag 7",
      "Tag 8",
      "Tag 9",
      "Tag 10",
    ],
  },
};

export const Inverted: Story = {
  args: {
    ...Default.args,
    inverted: true,
  },
};
