import { TagGroup, TagGroupProps } from "@/src/components/v2/TagGroup/TagGroup";
import { Meta, StoryObj } from "@kachurun/storybook-solid";

const meta: Meta<TagGroupProps> = {
  title: "Components/TagGroup",
  component: TagGroup,
  decorators: [
    (Story: StoryObj) => (
      /* for some reason w-x from tailwind was not working */
      <div style="width: 196px">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<TagGroupProps>;

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
