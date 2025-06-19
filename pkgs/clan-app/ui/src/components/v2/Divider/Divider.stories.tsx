import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { Divider, DividerProps } from "@/src/components/v2/Divider/Divider";

const meta: Meta<DividerProps> = {
  title: "Components/Divider",
  component: Divider,
};

export default meta;

type Story = StoryObj<DividerProps>;

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
    (Story: Story) => (
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
  decorators: [...Vertical.decorators],
};
