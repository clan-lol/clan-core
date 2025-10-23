import { Meta, StoryObj } from "storybook-solidjs-vite";
import { Divider } from "@/src/components/Divider/Divider";

const meta: Meta<typeof Divider> = {
  title: "Components/Divider",
  component: Divider,
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Horizontal: Story = {
  args: {
    orientation: "horizontal",
  },
};

export const HorizontalInverted: Story = {
  args: {
    inverted: true,
    ...Horizontal.args,
  },
};

export const Vertical: Story = {
  args: {
    orientation: "vertical",
  },
  decorators: [
    (Story) => (
      <div class="h-32 w-full">
        <Story />
      </div>
    ),
  ],
};

export const VerticalInverted: Story = {
  args: {
    inverted: true,
    ...Vertical.args,
  },
  decorators: Vertical.decorators,
};
